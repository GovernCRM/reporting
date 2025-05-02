import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def login(username: str, password: str) -> dict:
    """
    Authenticate with Buildly using username and password.
    """
    base_url = os.getenv("BASE_URL", "https://governcrm-api.buildly.dev")
    login_url = f"{base_url}/oauth/login/"
    
    # Get client credentials
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID or CLIENT_SECRET are not set in the environment variables.")
    
    try:
        # First try login without client credentials
        auth_data = {
            "username": username.strip() if username else "",
            "password": password.strip() if password else "",
            "client_id": client_id,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        print("Attempting login...")
        print(f"URL: {login_url}")
        print(f"Headers: {headers}")
        print(f"Data: {auth_data}")  # Ensure data is correctly formatted
        if not auth_data["username"]:
            raise ValueError("Username cannot be empty.")
        if not auth_data["password"]:
            raise ValueError("Password cannot be empty.")
        
        response = requests.post(
            login_url,
            data=auth_data,
            headers=headers
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {response_data}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 401:
            print("First attempt failed, trying with client credentials...")
            # Try again with client credentials
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
            
            print(f"Second attempt Status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Second attempt Body: {response_data}")
            except:
                print(f"Second attempt Text: {response.text}")
                
        response.raise_for_status()
        token_data = response.json()
        
        if "token" not in token_data and "access_token" not in token_data:
            raise ValueError(f"Unexpected response format: {token_data}")
            
        # Get the token from either format
        token = token_data.get("access_token_jwt") or token_data.get("access_token") or token_data.get("token")
        
        # Get user info
        print("Getting user info...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        user_response = requests.get(
            f"{base_url}/coreuser/me/",
            headers=headers
        )
        
        print(f"User info Status: {user_response.status_code}")
        try:
            user_data = user_response.json()
            print(f"User info Body: {user_data}")
        except:
            print(f"User info Text: {user_response.text}")
            
        user_response.raise_for_status()
        
        # Handle user data response
        if isinstance(user_data, list) and len(user_data) > 0:
            user_data = user_data[0]
            
        # Add token to user data
        user_data.update({
            "active": True,
            "access_token": token
        })
        
        return user_data
        
    except requests.exceptions.HTTPError as http_err:
        error_msg = str(http_err)
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if "error" in error_data:
                    error_msg = error_data["error"]
                elif "detail" in error_data:
                    error_msg = error_data["detail"]
        except:
            pass
        raise ValueError(f"Login failed: {error_msg}")
    except requests.exceptions.RequestException as req_err:
        raise ValueError(f"Connection error: {req_err}")
    except Exception as e:
        raise ValueError(f"Login failed: {str(e)}")
