from datetime import timedelta, datetime
import warnings
import time
import sys
import signal
import os
import traceback
from fitbit_utils import convert_str_to_date, get_todays_date, get_yesterday_date
from fitbit_auth import load_config, get_fitbit_instance
from fitbit_daily_data import (
    fetch_sleep_yesterday, 
    fetch_steps_yesterday, 
    fetch_rhr_yesterday,
    fetch_active_zone_minutes,
    fetch_activities
)
from supabase_utils import (
    get_supabase_client, 
    insert_fitbit_data, 
    get_last_recorded_date,
    authenticate_supabase,
    insert_activities,
    cleanup_supabase_client
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

def signal_handler(signum, frame):
    """Handle exit signals gracefully."""
    logger.info("Received exit signal, cleaning up...")
    cleanup_supabase_client()
    os._exit(0)  # Force exit immediately

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def fetch_data_safely(fetch_func, fitbit_client, date, data_type):
    """Safely fetch data with error handling."""
    try:
        data = fetch_func(fitbit_client, date)
        if data:
            logger.info(f"{data_type} data fetched successfully")
            return data
        else:
            logger.warning(f"No {data_type} data available for {date}")
            return None
    except Exception as e:
        logger.error(f"Error fetching {data_type} data: {type(e).__name__}")
        return None

def insert_data_safely(insert_func, *args, data_type):
    """Safely insert data with error handling."""
    try:
        insert_func(*args)
        logger.info(f"{data_type} data inserted successfully")
        return True
    except Exception as e:
        logger.error(f"Error inserting {data_type} data: {type(e).__name__}")
        return False

def main():
    try:
        # Initialize Supabase client and authenticate
        supabase = get_supabase_client()
        user_id = authenticate_supabase(supabase)
        logger.info("Successfully authenticated with Supabase")
        
        # Load config and get Fitbit client
        config = load_config()
        fitbit_client = get_fitbit_instance(config, supabase, user_id)
        
        # Get last recorded date from Supabase
        last_recorded_date = get_last_recorded_date(supabase, user_id)
        yesterday = get_yesterday_date()

        if last_recorded_date is None:
            logger.info("No previous data found. Starting fresh data collection.")
            last_recorded_date = yesterday
        else:
            logger.info(f"Last recorded date: {last_recorded_date}")

        # Fetch and store data for yesterday
        logger.info("Fetching yesterday's data...")
        date_str = yesterday.strftime('%Y-%m-%d')
        
        # Fetch sleep data
        logger.info("Fetching sleep data...")
        sleep_data = fetch_data_safely(fetch_sleep_yesterday, fitbit_client, yesterday, "Sleep")
        
        # Fetch steps data
        logger.info("Fetching steps data...")
        steps_data = fetch_data_safely(fetch_steps_yesterday, fitbit_client, yesterday, "Steps")
        
        # Fetch RHR data
        logger.info("Fetching RHR data...")
        rhr_data = fetch_data_safely(fetch_rhr_yesterday, fitbit_client, yesterday, "RHR")
        
        # Fetch Active Zone Minutes data
        logger.info("Fetching Active Zone Minutes data...")
        azm_data = fetch_data_safely(fetch_active_zone_minutes, fitbit_client, yesterday, "Active Zone Minutes")
        
        # Insert all data at once
        if any([sleep_data, steps_data, rhr_data, azm_data]):
            insert_data_safely(
                insert_fitbit_data,
                supabase,
                user_id,
                date_str,
                steps_data.get('summary', {}).get('steps', 0) if steps_data else 0,
                rhr_data if rhr_data else 0,
                sleep_data if sleep_data else "0h0min",
                azm_data.get('fat_burn', 0) if azm_data else 0,
                azm_data.get('cardio', 0) if azm_data else 0,
                azm_data.get('peak', 0) if azm_data else 0,
                data_type="Fitbit"
            )

        # Fetch and insert Activities data
        logger.info("Fetching Activities data...")
        activities_data = fetch_data_safely(fetch_activities, fitbit_client, yesterday, "Activities")
        if activities_data:
            insert_data_safely(insert_activities, supabase, user_id, yesterday, activities_data, data_type="Activities")

        logger.info("Script completed successfully")
        cleanup_supabase_client()
        os._exit(0)  # Force exit immediately

    except Exception as e:
        logger.error(f"An error occurred during script execution: {type(e).__name__}")
        logger.debug(f"Error details: {traceback.format_exc()}")
        cleanup_supabase_client()
        os._exit(1)  # Force exit with error code

if __name__ == "__main__":
    main()
