import streamlit as st
import pandas as pd
import requests
import json
from app.db import save_report, get_reports
import os

@st.cache_data(ttl=300)
def get_api_endpoints(token: str):
    api_docs_url = os.getenv("API_DOCS_URL")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(api_docs_url, headers=headers)
        response.raise_for_status()
        openapi = response.json()
        paths = openapi.get("paths", {})
        return [path for path, info in paths.items() if "get" in info]
    except Exception as e:
        st.error(f"Failed to fetch API docs: {e}")
        return []

def render_dashboard(token):
    user_data = st.session_state.get("user_data", {})
    org_id = user_data.get("organization", {}).get("organization_uuid")

    if not org_id:
        st.error("Unable to retrieve organization ID. Please try logging in again.")
        return

    st.title("📊 Build Custom Report")

    st.markdown("### Load Data from API")
    available_endpoints = get_api_endpoints(token)

    if not available_endpoints:
        st.warning("No GET endpoints found or failed to fetch API documentation.")
        return

    # Filter out buildly-core endpoints
    excluded_keywords = [
        "coregroups", "coreuser", "coreuser_me", "coreuser_notification", 
        "coreuser_reset_password", "coreuser_verify_email", "coreuser_read", 
        "coreuser_update", "coreuser_partial_update", "coreuser_update_profile", 
        "datamesh", "logicmodule", "oauth", "oauth_applications_update", 
        "oauth_login_create", "organization", "partner"
    ]
    filtered_endpoints = [
        endpoint for endpoint in available_endpoints 
        if not any(keyword in endpoint for keyword in excluded_keywords)
    ]

    # Simplify endpoint names for display
    simplified_endpoints = {
        endpoint: endpoint.split("/")[-1].replace("_", " ").title() or endpoint 
        for endpoint in filtered_endpoints
    }

    if not simplified_endpoints:
        st.warning("No relevant API endpoints available.")
        return

    selected_endpoint = st.selectbox("Choose an API endpoint", options=list(simplified_endpoints.keys()), format_func=lambda x: simplified_endpoints[x])

    if st.button("Load Data"):
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            base_url = os.getenv("BASE_URL")
            url = f"{base_url}{selected_endpoint}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and isinstance(data[0], dict):
                df = pd.json_normalize(data)
            else:
                df = pd.DataFrame(data)

            st.success("Data loaded successfully!")
            st.dataframe(df)
            st.session_state["loaded_data"] = df
            st.session_state["available_columns"] = list(df.columns)
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            return
    else:
        if "loaded_data" not in st.session_state:
            st.warning("Please load data to proceed.")
            return

    df = st.session_state.get("loaded_data")
    if df is not None:
        st.markdown("### Create Report")
        name = st.text_input("Report Name")
        available_columns = st.session_state.get("available_columns", [])
        filters = {}

        for column in available_columns:
            try:
                unique_values = df[column].dropna().unique()
                if not all(isinstance(v, (str, int, float, bool, type(None))) for v in unique_values):
                    continue
            except TypeError:
                continue

            if len(unique_values) > 1 and len(unique_values) <= 50:
                selected_value = st.selectbox(f"Filter by {column}", ["All"] + sorted(map(str, unique_values.tolist())))
                if selected_value != "All":
                    filters[column] = selected_value
            elif len(unique_values) > 50:
                input_value = st.text_input(f"Filter by {column} (exact match)")
                if input_value:
                    filters[column] = input_value

        date_columns = [col for col in available_columns if "date" in col.lower()]
        if date_columns:
            selected_date_col = st.selectbox("Select Date Column", date_columns) if len(date_columns) > 1 else date_columns[0]
            date_range = st.date_input("Date Range", [])
            if isinstance(date_range, list) and len(date_range) == 2:
                filters["date_column"] = selected_date_col
                filters["date_range"] = [str(d) for d in date_range]
            elif isinstance(date_range, pd._libs.tslibs.timestamps.Timestamp) or isinstance(date_range, pd.Timestamp):
                filters["date_column"] = selected_date_col
                filters["date_range"] = [str(date_range), str(date_range)]

        if st.button("Run Report"):
            filtered = df.copy()
            for key, value in filters.items():
                if key == "date_range":
                    continue
                filtered = filtered[filtered[key] == value]

            if "date_range" in filters:
                date_col = filters["date_column"]
                start_date, end_date = filters["date_range"]
                filtered[date_col] = pd.to_datetime(filtered[date_col], errors='coerce')
                filtered = filtered[
                    (filtered[date_col].dt.date >= pd.to_datetime(start_date).date()) &
                    (filtered[date_col].dt.date <= pd.to_datetime(end_date).date())
                ]

            st.dataframe(filtered)

            st.download_button("📥 Export to CSV", filtered.to_csv(index=False), file_name="report.csv")

            if name:
                save_report(org_id, name, filters)
                st.success(f"Report '{name}' saved!")

            # Aggregation & sorting
            st.markdown("### 📊 Charts & Aggregation")
            st.markdown("#### Coming Soon!")
            numeric_cols = filtered.select_dtypes(include=["int", "float"]).columns.tolist()
            if numeric_cols:
                group_col = st.selectbox("Group By Column", available_columns)
                agg_col = st.selectbox("Numeric Column", numeric_cols)
                agg_func = st.selectbox("Aggregation Function", ["sum", "mean", "count"])
                sort_order = st.radio("Sort Order", ["Descending", "Ascending"])

                if group_col and agg_col:
                    agg_map = {
                        "sum": "sum",
                        "mean": "mean",
                        "count": "count"
                    }
                    chart_df = filtered.groupby(group_col)[agg_col].agg(agg_map[agg_func]).reset_index()
                    chart_df = chart_df.sort_values(by=agg_col, ascending=(sort_order == "Ascending"))

                    st.bar_chart(chart_df.set_index(group_col))
                    st.line_chart(chart_df.set_index(group_col))

                    st.markdown("Pie Chart")
                    st.plotly_chart({
                        "data": [{
                            "type": "pie",
                            "labels": chart_df[group_col],
                            "values": chart_df[agg_col]
                        }]
                    })

                    # Save visualization definition (optional)
                    if st.checkbox("Save this visualization definition"):
                        viz = {
                            "group_by": group_col,
                            "metric": agg_col,
                            "agg_func": agg_func,
                            "sort_order": sort_order
                        }
                        with open(f"viz_{name or 'unnamed'}.json", "w") as f:
                            json.dump(viz, f)
                        st.success("Visualization saved locally.")

        st.markdown("## 🗂️ Your Reports")
        reports = get_reports(org_id)
        for r in reports:
            with st.expander(f"{r['name']} ({r['created_at']})"):
                q = r["query"]
                filtered = df.copy()
                for key, value in q.items():
                    if key not in ["date_range", "date_column"]:
                        filtered = filtered[filtered[key] == value]
                if "date_range" in q:
                    date_col = q["date_column"]
                    start_date, end_date = q["date_range"]
                    filtered[date_col] = pd.to_datetime(filtered[date_col], errors='coerce')
                    filtered = filtered[
                        (filtered[date_col].dt.date >= pd.to_datetime(start_date).date()) &
                        (filtered[date_col].dt.date <= pd.to_datetime(end_date).date())
                    ]
                st.dataframe(filtered)
