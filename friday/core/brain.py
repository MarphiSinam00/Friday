# core/brain.py
from core.connectivity import is_online
from core.offline_llm import chat as offline_chat
from core.context import build_system_prompt
from config.settings import FRIDAY_NAME
import re


SKILL_TRIGGERS = {
    "open_youtube": ["open youtube", "play youtube", "go to youtube"],
    "open_spotify": ["open spotify", "play spotify", "play music", "open music"],
    "open_netflix": ["open netflix", "watch netflix"],
    "open_whatsapp": ["open whatsapp", "whatsapp"],
    "open_app": ["open ", "launch ", "start "],
    "bored": ["i'm bored", "im bored", "i am bored", "so bored", "nothing to do", "entertain me"],
    "reminder": ["remind me", "set a reminder", "set reminder"],
    "screenshot": ["take a screenshot", "screenshot", "what's on my screen", "what is on my screen"],
    "read_file": ["read this file", "read the file", "open and read"],
}


def detect_skill(text: str) -> str | None:
    """Detect if user input matches a skill trigger."""
    text_lower = text.lower().strip()
    for skill, triggers in SKILL_TRIGGERS.items():
        for trigger in triggers:
            if trigger in text_lower:
                return skill
    return None


def extract_app_name(text: str) -> str:
    """Extract app name from open/launch commands."""
    text_lower = text.lower()
    for prefix in ["open ", "launch ", "start "]:
        if prefix in text_lower:
            return text_lower.split(prefix, 1)[1].strip()
    return ""


def think(messages: list[dict]) -> tuple[str, bool]:
    """
    Main entry point. Routes to skills or LLM.
    Returns (response_text, was_online).
    """
    last_message = messages[-1]["content"] if messages else ""
    skill = detect_skill(last_message)

    if skill:
        response = handle_skill(skill, last_message)
        if response:
            return response, is_online()

    system_prompt = build_system_prompt()
    online = is_online()

    if online:
        try:
            response = _online_think(messages, system_prompt)
            _check_and_save_name(messages)
            return response, True
        except Exception as e:
            print(f"[{FRIDAY_NAME}] Online brain failed, falling back: {e}")

    response = offline_chat(messages, system_prompt)
    _check_and_save_name(messages)
    return response, False


def handle_skill(skill: str, text: str) -> str | None:
    """Execute a skill and return response."""
    try:
        if skill == "open_youtube":
            from skills.os_control import open_youtube
            query = text.lower().replace("open youtube", "").replace("play youtube", "").strip()
            return open_youtube(query)

        elif skill == "open_spotify":
            from skills.os_control import open_spotify
            return open_spotify()

        elif skill == "open_netflix":
            from skills.os_control import open_netflix
            return open_netflix()

        elif skill == "open_whatsapp":
            from skills.os_control import open_whatsapp
            return open_whatsapp()

        elif skill == "open_app":
            from skills.os_control import open_app
            app_name = extract_app_name(text)
            if app_name:
                return open_app(app_name)

        elif skill == "bored":
            from skills.bored_mode import handle_bored
            from skills.os_control import open_spotify, open_youtube, open_netflix
            response, action = handle_bored()
            if action:
                try:
                    action()
                except Exception as e:
                    print(f"[Friday] Bored mode action failed: {e}")
            return response

        elif skill == "reminder":
            from skills.scheduler import parse_reminder, add_reminder
            parsed = parse_reminder(text)
            if parsed:
                message, minutes = parsed
                def _fire_reminder(msg):
                    from voice.speaker import speak
                    speak(f"Sir, this is your reminder — {msg}", online=is_online())
                return add_reminder(message, minutes, _fire_reminder)
            return "I could not quite parse that reminder, Sir. Could you say it again?"

        elif skill == "screenshot":
            from skills.screen_vision import capture_and_describe
            filepath, _ = capture_and_describe()
            if filepath:
                return f"Screenshot taken and saved, Sir. You can find it in your Pictures folder."
            return "I was unable to take a screenshot, Sir."

    except Exception as e:
        print(f"[Friday] Skill error: {e}")

    return None


def _online_think(messages: list[dict], system_prompt: str) -> str:
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        from core.offline_llm import chat as offline_chat
        return offline_chat(messages, system_prompt)
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text.strip()


def _check_and_save_name(messages: list[dict]):
    from memory.user_profile import set_profile
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"].lower()
            if "my name is" in content:
                parts = content.split("my name is")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0].capitalize()
                    set_profile("user_real_name", name)
