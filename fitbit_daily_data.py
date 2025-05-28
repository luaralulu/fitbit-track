from fitbit_utils import calculate_sleep_metrics
from datetime import datetime, timedelta

def fetch_steps_yesterday(fitbit_client, date):
    """Fetch steps data for a specific date."""
    return fitbit_client.activities(date=date)

def fetch_sleep_yesterday(fitbit_client, date):
    """Fetch sleep data for a specific date."""
    sleep_data = fitbit_client.sleep(date=date)
    if sleep_data and 'sleep' in sleep_data and sleep_data['sleep']:
        total_sleep_minutes = sum(sleep['minutesAsleep'] for sleep in sleep_data['sleep'])
        hours = total_sleep_minutes // 60
        minutes = total_sleep_minutes % 60
        return f"{hours}h{minutes}min"
    return "0h0min"

def fetch_rhr_yesterday(fitbit_client, date):
    """Fetch resting heart rate data for a specific date."""
    heart_data = fitbit_client.intraday_time_series('activities/heart', base_date=date, detail_level='1min')
    if heart_data and 'activities-heart' in heart_data and heart_data['activities-heart']:
        return heart_data['activities-heart'][0]['value']['restingHeartRate']
    return 0

def fetch_active_zone_minutes(fitbit_client, date):
    """Fetch active zone minutes for a specific date."""
    try:
        # Get active zone minutes data
        zone_data = fitbit_client.intraday_time_series('activities/heart', base_date=date, detail_level='1min')
        if zone_data and 'activities-heart-intraday' in zone_data:
            # Calculate total minutes in each zone
            zones = {
                'fat_burn': 0,
                'cardio': 0,
                'peak': 0
            }
            
            for minute in zone_data['activities-heart-intraday']['dataset']:
                if minute['value'] >= 140:  # Peak zone
                    zones['peak'] += 1
                elif minute['value'] >= 120:  # Cardio zone
                    zones['cardio'] += 1
                elif minute['value'] >= 100:  # Fat burn zone
                    zones['fat_burn'] += 1
            
            return zones
    except Exception as e:
        print(f"Error fetching active zone minutes: {e}")
    return {'fat_burn': 0, 'cardio': 0, 'peak': 0}

def fetch_activities(fitbit_client, date):
    """Fetch activities for a specific date."""
    try:
        activities = fitbit_client.activities(date=date)
        if activities and 'activities' in activities:
            return [{
                'name': activity['name'],
                'duration': activity['duration'],
                'calories': activity['calories'],
                'distance': activity.get('distance', 0),
                'start_time': activity['startTime']
            } for activity in activities['activities']]
    except Exception as e:
        print(f"Error fetching activities: {e}")
    return []
