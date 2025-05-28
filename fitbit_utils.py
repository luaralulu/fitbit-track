import datetime
from datetime import timedelta

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

def get_yesterday_date():
    today = datetime.date.today()
    yesterday = today - timedelta(days=1)

    return yesterday

def get_todays_date():
    return datetime.date.today()

def convert_str_to_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()