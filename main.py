import streamlit as st
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def health_check():
    return {"status": "ok"}

if st.experimental_get_query_params().get("health_check"):
    st.json(health_check())

from app.ui import render_dashboard
from app.db import init_db
from app.auth import login
import os

st.title(os.getenv("PAGE_TITLE", "Buildly Reporting"))
st.caption("Powered by Buildly Open Core")

with st.form("login_form"):
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        with st.spinner("Logging in..."):
            try:
                logging.info("Attempting login for user: %s", username)
                user_data = login(username, password)
                st.session_state["user_data"] = user_data
                st.success("Login successful!")
                with st.spinner("Loading dashboard..."):
                    init_db()
                    render_dashboard(user_data["access_token"])
            except ValueError as e:
                logging.error("Login failed: %s", str(e))
                st.error(f"Login failed: {str(e)}")
                st.info("Please check your credentials and try again.")
            except Exception as e:
                logging.exception("Unexpected error during login")
                st.error(f"Unexpected error: {str(e)}")
elif "user_data" in st.session_state:
    with st.spinner("Loading dashboard..."):
        try:
            init_db()
            render_dashboard(st.session_state["user_data"]["access_token"])
        except Exception as e:
            logging.exception("Error loading dashboard")
            st.error(f"Error loading dashboard: {str(e)}")

st.markdown("---")
st.markdown("""
    Having trouble logging in?
    - Make sure you're using your Buildly account credentials
    - Check that your username/email and password are correct
    """)
