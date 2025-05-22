import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def login(username: str, password: str) -> dict:
    base_url = os.getenv("BASE_URL", "https://governcrm-api.buildly.dev")
    login_url = f"{base_url}/oauth/login/"
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    if not client_id or not client_secret:
        logger.error("CLIENT_ID or CLIENT_SECRET are not set in the environment variables.")
        raise ValueError("CLIENT_ID or CLIENT_SECRET are not set in the environment variables.")
    try:
        auth_data = {
            "username": username.strip() if username else "",
            "password": password.strip() if password else "",
            "client_id": client_id,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        logger.info("Attempting login at %s", login_url)
        response = requests.post(
            login_url,
            data=auth_data,
            headers=headers
        )
        logger.info("Login response status: %s", response.status_code)
        if response.status_code == 401:
            logger.warning("First login attempt failed, retrying with client_secret")
            auth_data.update({
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret
            })
            response = requests.post(
                login_url,
                json=auth_data,
                headers=headers
            )
            logger.info("Second login attempt status: %s", response.status_code)
        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("access_token_jwt") or token_data.get("access_token") or token_data.get("token")
        logger.info("Token received, fetching user info")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        user_response = requests.get(
            f"{base_url}/coreuser/me/",
            headers=headers
        )
        logger.info("User info response status: %s", user_response.status_code)
        user_response.raise_for_status()
        user_data = user_response.json()
        if isinstance(user_data, list) and len(user_data) > 0:
            user_data = user_data[0]
        user_data.update({
            "active": True,
            "access_token": token
        })
        return user_data
    except Exception as e:
        logger.exception("Login failed")
        raise ValueError(f"Login failed: {str(e)}")