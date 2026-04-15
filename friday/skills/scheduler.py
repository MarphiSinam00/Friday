# skills/scheduler.py
import threading
import time
from datetime import datetime, timedelta
from typing import Callable


_reminders = []
_lock = threading.Lock()


def add_reminder(message: str, minutes: int, callback: Callable) -> str:
    """Add a reminder to fire after N minutes."""
    trigger_time = datetime.now() + timedelta(minutes=minutes)
    reminder = {
        "message": message,
        "trigger_time": trigger_time,
        "callback": callback,
    }
    with _lock:
        _reminders.append(reminder)
    return f"Reminder set for {trigger_time.strftime('%I:%M %p')}, Sir. I will let you know."


def add_reminder_at_time(message: str, hour: int, minute: int, callback: Callable) -> str:
    """Add a reminder for a specific time today."""
    now = datetime.now()
    trigger = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if trigger < now:
        trigger += timedelta(days=1)
    reminder = {
        "message": message,
        "trigger_time": trigger,
        "callback": callback,
    }
    with _lock:
        _reminders.append(reminder)
    return f"Reminder set for {trigger.strftime('%I:%M %p')}, Sir."


def _reminder_loop():
    """Background thread that checks and fires reminders."""
    while True:
        now = datetime.now()
        with _lock:
            fired = []
            for reminder in _reminders:
                if now >= reminder["trigger_time"]:
                    try:
                        reminder["callback"](reminder["message"])
                    except Exception as e:
                        print(f"[Friday Reminder] Error: {e}")
                    fired.append(reminder)
            for r in fired:
                _reminders.remove(r)
        time.sleep(10)


def start():
    """Start the reminder background thread."""
    t = threading.Thread(target=_reminder_loop, daemon=True)
    t.start()
    print("[Friday] Reminder scheduler started.")


def parse_reminder(text: str) -> tuple[str, int] | None:
    """
    Parse reminder from natural language.
    Returns (message, minutes) or None.
    Examples:
    - "remind me in 5 minutes to drink water" -> ("drink water", 5)
    - "remind me to eat lunch in 30 minutes" -> ("eat lunch", 30)
    """
    text = text.lower()
    import re

    # Pattern: "in X minutes"
    match = re.search(r'in (\d+) minutes?', text)
    if match:
        minutes = int(match.group(1))
        # Extract the message
        message = re.sub(r'remind me (to |in \d+ minutes? )?', '', text)
        message = re.sub(r'in \d+ minutes?', '', message).strip()
        return message, minutes

    # Pattern: "in X hours"
    match = re.search(r'in (\d+) hours?', text)
    if match:
        hours = int(match.group(1))
        message = re.sub(r'remind me (to |in \d+ hours? )?', '', text)
        message = re.sub(r'in \d+ hours?', '', message).strip()
        return message, hours * 60

    return None
