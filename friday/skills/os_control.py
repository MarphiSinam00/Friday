# skills/os_control.py
import subprocess
import os
import webbrowser
from pathlib import Path
from skills.app_finder import find_app, get_chrome_path, get_browser_url


def open_app(app_name: str) -> str:
    """
    Smart app opener. Checks local installation first,
    falls back to Chrome browser if not found locally.
    """
    name = app_name.lower().strip()

    # Check local installation first
    local_path = find_app(name)
    if local_path:
        try:
            subprocess.Popen([local_path])
            return f"Opening {app_name} locally, Sir."
        except Exception as e:
            print(f"[Friday OS] Local open failed: {e}")

    # Try Windows Start Menu search
    try:
        result = _open_via_start_menu(name)
        if result:
            return f"Opening {app_name}, Sir."
    except Exception:
        pass

    # Fall back to browser URL
    url = get_browser_url(name)
    if url:
        return open_url(url, f"{app_name}")

    # Last resort - open Chrome with search
    return open_url(f"https://www.google.com/search?q={app_name}", app_name)


def _open_via_start_menu(app_name: str) -> bool:
    """Try to open app via Windows shell."""
    try:
        os.startfile(app_name)
        return True
    except Exception:
        pass
    try:
        subprocess.Popen(["start", app_name], shell=True)
        return True
    except Exception:
        return False


def open_url(url: str, label: str = "") -> str:
    """Open a URL in Chrome or default browser."""
    chrome_path = get_chrome_path()
    try:
        if chrome_path:
            subprocess.Popen([chrome_path, url])
        else:
            webbrowser.open(url)
        name = label if label else url
        return f"Opening {name} in your browser, Sir."
    except Exception as e:
        return f"I encountered an issue opening that, Sir. {e}"


def open_youtube(query: str = "") -> str:
    """Open YouTube, optionally with a search query."""
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return open_url(url, f"YouTube search for {query}")
    return open_url("https://www.youtube.com", "YouTube")


def open_spotify() -> str:
    """Open Spotify locally or in browser."""
    return open_app("spotify")


def open_whatsapp(contact: str = "") -> str:
    """Open WhatsApp desktop or web."""
    local = find_app("whatsapp")
    if local:
        subprocess.Popen([local])
        return "Opening WhatsApp, Sir."
    return open_url("https://web.whatsapp.com", "WhatsApp")


def open_netflix() -> str:
    """Open Netflix in browser."""
    return open_url("https://www.netflix.com", "Netflix")


def open_file(file_path: str) -> str:
    """Open any file with its default application."""
    try:
        os.startfile(file_path)
        return f"Opening that file for you, Sir."
    except Exception as e:
        return f"I could not open that file, Sir. {e}"


def open_folder(folder_path: str) -> str:
    """Open a folder in Windows Explorer."""
    try:
        subprocess.Popen(["explorer", folder_path])
        return f"Opening that folder, Sir."
    except Exception as e:
        return f"I could not open that folder, Sir. {e}"


def run_command(command: str) -> str:
    """Run a terminal command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output if output else "Command executed, Sir."
    except subprocess.TimeoutExpired:
        return "That command took too long, Sir."
    except Exception as e:
        return f"Command failed, Sir. {e}"


def take_screenshot() -> str:
    """Take a screenshot and save it. Returns file path."""
    try:
        import PIL.ImageGrab as ImageGrab
        from datetime import datetime
        screenshots_dir = Path.home() / "Pictures" / "Friday_Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        filename = f"friday_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = screenshots_dir / filename
        img = ImageGrab.grab()
        img.save(str(filepath))
        return str(filepath)
    except Exception as e:
        print(f"[Friday] Screenshot failed: {e}")
        return ""


def set_volume(level: int) -> str:
    """Set system volume 0-100."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level} percent, Sir."
    except Exception:
        return f"I could not adjust the volume, Sir."
