# skills/screen_vision.py
from skills.os_control import take_screenshot
from pathlib import Path


def capture_and_describe() -> tuple[str, str]:
    try:
        from skills.os_control import take_screenshot
        import os
        filepath = take_screenshot()
        if filepath and os.path.exists(filepath):
            return filepath, f"Screenshot saved to your Desktop in Friday_Screenshots folder Sir."
        return "", "I was unable to capture the screen Sir."
    except Exception as e:
        return "", f"Screenshot failed Sir. {e}"


def get_screen_context() -> str:
    """Get what's currently on screen as context for Friday."""
    try:
        import PIL.ImageGrab as ImageGrab
        import PIL.Image as Image
        img = ImageGrab.grab()
        # Get dominant colors and basic info
        width, height = img.size
        return f"Screen resolution: {width}x{height}"
    except Exception as e:
        return f"Screen capture unavailable: {e}"
