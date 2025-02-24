
from datetime import datetime, timedelta


def checkBdayToday(bday:int):
    bday_date = datetime.fromtimestamp(bday)
    
    # Get today's date
    today = datetime.today()
    
    # Compare only month and day
    return (bday_date.month, bday_date.day) == (today.month, today.day)

def secondsUntil12h(timestampStart:int):
    start_time = datetime.fromtimestamp(timestampStart)

    # Add 14 hours to the start time
    target_time = start_time + timedelta(hours=12)

    # Get current time
    now = datetime.now()

    # Calculate the difference in seconds
    remaining_seconds = (target_time - now).total_seconds()
    # If time has already passed, return 0
    return max(0, int(remaining_seconds))