import gather_keys_oauth2 as Oauth2
import json
import fitbit
import os
from dotenv import load_dotenv
from supabase_utils import get_fitbit_tokens, update_fitbit_tokens
import logging

logger = logging.getLogger(__name__)

def load_config():
    """Load Config from environment variables."""
    # Only load .env file in local environment
    if not os.getenv('GITHUB_ACTIONS'):
        load_dotenv()
    
    required_vars = [
        "FITBIT_CLIENT_ID",
        "FITBIT_CLIENT_SECRET"
    ]
    
    # Check if all required variables are present
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        "fitbit_api_keys": {
            "client_id": os.getenv("FITBIT_CLIENT_ID"),
            "client_secret": os.getenv("FITBIT_CLIENT_SECRET")
        }
    }

def update_tokens(supabase, user_id, new_tokens):
    """Update the access and refresh tokens in Supabase."""
    logger.info("Updating Fitbit tokens in Supabase")
    update_fitbit_tokens(
        supabase,
        user_id,
        new_tokens["access_token"],
        new_tokens["refresh_token"],
        new_tokens["expires_at"]
    )
    logger.info("Tokens updated successfully")

def get_fitbit_instance(credentials, supabase, user_id):
    client_id = credentials["fitbit_api_keys"]["client_id"]
    client_secret = credentials["fitbit_api_keys"]["client_secret"]
    
    # Get tokens from Supabase
    tokens = get_fitbit_tokens(supabase, user_id)
    if not tokens:
        if os.getenv('GITHUB_ACTIONS'):
            raise Exception("No Fitbit tokens found in database. Please run the authentication process locally first.")
        else:
            raise Exception("No Fitbit tokens found in database. Please authenticate first.")
    
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    def token_update_callback(new_token):
        """Callback function to handle token refresh."""
        logger.info("Received new Fitbit token")
        update_tokens(supabase, user_id, new_token)

    return fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=access_token,
        refresh_token=refresh_token,
        refresh_cb=token_update_callback
    )

def authenticate_fitbit(credentials, supabase, user_id):
    """Authenticate and return a Fitbit client instance."""
    if os.getenv('GITHUB_ACTIONS'):
        raise Exception("Authentication must be performed locally. Please run the authentication process on your local machine first.")
        
    client_id = credentials["fitbit_api_keys"]["client_id"]
    client_secret = credentials["fitbit_api_keys"]["client_secret"]

    logger.info("Starting Fitbit authentication process")
    server = Oauth2.OAuth2Server(client_id, client_secret)
    server.browser_authorize()

    # Extract the authorization code from the server response
    authorization_code = 'xxx'
    logger.info("Authorization code received")

    # Use the new method to get tokens
    tokens = server.get_tokens(authorization_code)
    logger.info("Successfully obtained Fitbit tokens")
    
    # Store tokens in Supabase
    update_tokens(supabase, user_id, tokens)
    
    return tokens
