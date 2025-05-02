import streamlit as st
from app.ui import render_dashboard
from app.db import init_db
from app.auth import login
import os

# Set page title
st.title(os.getenv("PAGE_TITLE", "Buildly Reporting"))
st.caption("Powered by Buildly Open Core")

# Create login form
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
                # Attempt to login and get user data
                user_data = login(username, password)
                # Store the token in session state for later use
                st.session_state["user_data"] = user_data
                
                # Show success message
                st.success("Login successful!")
                
                with st.spinner("Loading dashboard..."):
                    # Initialize database and render dashboard
                    init_db()
                    render_dashboard(user_data["access_token"])
                    
            except ValueError as e:
                st.error(f"Login failed: {str(e)}")
                st.info("Please check your credentials and try again.")
elif "user_data" in st.session_state:
    # If already logged in, show the dashboard
    with st.spinner("Loading dashboard..."):
        init_db()
        render_dashboard(st.session_state["user_data"]["access_token"])

# Add helpful message at the bottom
st.markdown("---")
st.markdown("""
    Having trouble logging in?
    - Make sure you're using your Buildly account credentials
    - Check that your username/email and password are correct
    """)
