from datetime import datetime

def display_current_day_time() -> str:
    now = datetime.now()
    day_of_week = now.strftime("%A")
    return f"{day_of_week}, {now.strftime('%H:%M:%S')}, {now.strftime('%Y-%m-%d')}"