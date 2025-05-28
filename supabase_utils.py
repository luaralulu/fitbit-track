import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from datetime import datetime
import atexit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client instance
_supabase_client = None

def load_supabase_config():
    """Load Supabase configuration from environment variables."""
    # Only load .env file in local environment
    if not os.getenv('GITHUB_ACTIONS'):
        load_dotenv()
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_USER_EMAIL",
        "SUPABASE_USER_PASSWORD"
    ]
    
    # Check if all required variables are present
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return {
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key to bypass RLS
    }

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        config = load_supabase_config()
        _supabase_client = create_client(config["url"], config["key"])
        # Register cleanup function
        atexit.register(cleanup_supabase_client)
    return _supabase_client

def cleanup_supabase_client():
    """Clean up the Supabase client connection."""
    global _supabase_client
    if _supabase_client is not None:
        try:
            # Close any open connections
            if hasattr(_supabase_client, 'rest') and hasattr(_supabase_client.rest, 'close'):
                _supabase_client.rest.close()
            _supabase_client = None
            logger.info("Supabase client connection closed")
        except Exception as e:
            logger.error(f"Error closing Supabase client: {e}")

def authenticate_supabase(supabase: Client) -> str:
    """Authenticate with Supabase and return the user ID."""
    try:
        # Get credentials from environment variables
        email = os.getenv("SUPABASE_USER_EMAIL")
        password = os.getenv("SUPABASE_USER_PASSWORD")
        
        if not email or not password:
            raise ValueError("Supabase credentials not found in environment variables")
        
        # Sign in
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        logger.info("Successfully authenticated with Supabase")
        return response.user.id
    except Exception as e:
        logger.error(f"Error authenticating with Supabase: {e}")
        raise

def insert_fitbit_data(supabase: Client, user_id: str, date: str, steps: int, heart_rate: int, sleep: str, 
                      fat_burn_minutes: int = 0, cardio_minutes: int = 0, peak_minutes: int = 0):
    """Insert or update Fitbit data in the Supabase table."""
    # Check if data already exists for this date
    existing_data = supabase.table("fitbit_data")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("date", date)\
        .execute()
    
    data = {
        "user_id": user_id,
        "date": date,
        "steps": steps,
        "heart_rate": heart_rate,
        "sleep": sleep,
        "fat_burn_minutes": fat_burn_minutes,
        "cardio_minutes": cardio_minutes,
        "peak_minutes": peak_minutes
    }
    
    if existing_data.data:
        existing_record = existing_data.data[0]
        if existing_record["steps"] == steps:
            logger.info(f"Data for {date} already exists with same steps, skipping...")
            return existing_data
        
        # Update existing record with new data
        logger.info(f"Updating existing data for {date} with new values")
        result = supabase.table("fitbit_data")\
            .update(data)\
            .eq("user_id", user_id)\
            .eq("date", date)\
            .execute()
    else:
        # Insert new record
        logger.info(f"Inserting new data for {date}")
        result = supabase.table("fitbit_data").insert(data).execute()
    
    return result

def insert_activities(supabase: Client, user_id: str, date, activities):
    """Insert activities into the Supabase table."""
    for activity in activities:
        try:
            start_time = datetime.strptime(activity['start_time'], '%H:%M')
            full_datetime = datetime.combine(date, start_time.time())
            formatted_time = full_datetime.isoformat()
        except Exception as e:
            logger.error(f"Error formatting time for activity {activity['name']}: {e}")
            continue

        # Check if activity already exists
        existing_activity = supabase.table("fitbit_activities")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("date", date.strftime('%Y-%m-%d'))\
            .eq("activity_name", activity['name'])\
            .eq("duration", activity['duration'])\
            .execute()

        if existing_activity.data:
            logger.info(f"Activity {activity['name']} already exists for {date.strftime('%Y-%m-%d')}, skipping...")
            continue

        data = {
            "user_id": user_id,
            "date": date.strftime('%Y-%m-%d'),
            "activity_name": activity['name'],
            "duration": activity['duration'],
            "calories": activity['calories'],
            "distance": activity['distance'],
            "start_time": formatted_time
        }
        supabase.table("fitbit_activities").insert(data).execute()
        logger.info(f"Inserted activity {activity['name']} for {date.strftime('%Y-%m-%d')}")

def get_last_recorded_date(supabase: Client, user_id: str) -> str:
    """Get the last recorded date from the Supabase table for a specific user."""
    result = supabase.table("fitbit_data")\
        .select("date")\
        .eq("user_id", user_id)\
        .order("date", desc=True)\
        .limit(1)\
        .execute()
    
    if result.data:
        return result.data[0]["date"]
    return None

def get_fitbit_tokens(supabase: Client, user_id: str):
    """Get the latest Fitbit tokens for a user."""
    result = supabase.table("fitbit_tokens")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    if result.data:
        return result.data[0]
    return None

def update_fitbit_tokens(supabase: Client, user_id: str, access_token: str, refresh_token: str, expires_at: float):
    """Update Fitbit tokens in the database."""
    data = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "fitbit_expires_at": expires_at,
        "updated_at": datetime.now().isoformat()
    }
    
    result = supabase.table("fitbit_tokens").insert(data).execute()
    return result 