import datetime
from datetime import timedelta
import pytz

def calculate_sleep_metrics(sleep_data):
    # Extract metrics from the API response
    minutes_asleep = sleep_data.get('minutesAsleep', 0)
    restless_duration = sleep_data.get('restlessDuration', 0)

    # Total sleep time
    total_sleep_time_minutes = minutes_asleep - restless_duration
    sleep_hours = total_sleep_time_minutes // 60
    sleep_minutes = total_sleep_time_minutes % 60
    formatted_sleep_time = f"{sleep_hours}h{sleep_minutes}min"

    return formatted_sleep_time

def get_aest_now():
    """Get current time in AEST timezone."""
    aest = pytz.timezone('Australia/Sydney')
    return datetime.datetime.now(aest)

def get_yesterday_date():
    """Get yesterday's date in AEST timezone."""
    now = get_aest_now()
    yesterday = now.date() - timedelta(days=1)
    return yesterday

def get_todays_date():
    """Get today's date in AEST timezone."""
    return get_aest_now().date()

def convert_str_to_date(date_str):
    """Convert string to date in AEST timezone."""
    aest = pytz.timezone('Australia/Sydney')
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    return date