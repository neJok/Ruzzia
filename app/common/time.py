from datetime import datetime
import pytz


def convert_to_iso8601(time_str: str, timezone: str) -> datetime:
    time_obj = datetime.strptime(time_str, '%H:%M').time()
    current_date = datetime.now().date()
    datetime_obj = datetime.combine(current_date, time_obj)
    tz = pytz.timezone(timezone)
    datetime_with_tz = tz.localize(datetime_obj)
    
    return datetime_with_tz
