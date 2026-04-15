from config.settings import FRIDAY_PERSONALITY, USER_NAME
from memory.user_profile import get_all_profile
from core.connectivity import is_online
from datetime import datetime


def build_system_prompt() -> str:
    profile = get_all_profile()
    
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
    
    mode_note = (
        "You are currently ONLINE. You can reference real-time information. Always summarize briefly."
        if is_online()
        else "You are currently OFFLINE. Work from local knowledge only."
    )

    profile_context = ""
    if profile:
        profile_lines = "\n".join([f"- {k}: {v}" for k, v in profile.items()])
        profile_context = f"\n\nWhat you know about Sir:\n{profile_lines}"

    return (
        f"{FRIDAY_PERSONALITY}\n\n"
        f"Current date: {current_date}\n"
        f"Current time: {current_time}\n\n"
        f"{mode_note}"
        f"{profile_context}"
    )
