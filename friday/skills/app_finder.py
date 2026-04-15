# skills/app_finder.py
import os
import winreg
from pathlib import Path


# Common app installation paths to check
APP_PATHS = {
    "spotify": [
        Path(os.environ.get("APPDATA", "")) / "Spotify" / "Spotify.exe",
        Path("C:/Program Files/Spotify/Spotify.exe"),
        Path("C:/Program Files (x86)/Spotify/Spotify.exe"),
    ],
    "youtube": [
        # YouTube is browser-based, no local app usually
    ],
    "netflix": [
        # Check Windows Store apps
    ],
    "whatsapp": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "WhatsApp" / "WhatsApp.exe",
        Path("C:/Program Files/WhatsApp/WhatsApp.exe"),
        Path(os.environ.get("APPDATA", "")) / "WhatsApp" / "WhatsApp.exe",
    ],
    "chrome": [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ],
    "discord": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Discord" / "Update.exe",
        Path(os.environ.get("APPDATA", "")) / "Discord" / "Update.exe",
    ],
    "steam": [
        Path("C:/Program Files (x86)/Steam/Steam.exe"),
        Path("C:/Program Files/Steam/Steam.exe"),
    ],
    "vscode": [
        Path("C:/Program Files/Microsoft VS Code/Code.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/Code.exe",
    ],
    "notepad": [
        Path("C:/Windows/System32/notepad.exe"),
    ],
    "calculator": [
        Path("C:/Windows/System32/calc.exe"),
    ],
    "vlc": [
        Path("C:/Program Files/VideoLAN/VLC/vlc.exe"),
        Path("C:/Program Files (x86)/VideoLAN/VLC/vlc.exe"),
    ],
}

BROWSER_URLS = {
    "youtube": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
}


def find_app(app_name: str) -> str | None:
    """Find the local executable path for an app. Returns path or None."""
    name = app_name.lower().strip()
    paths = APP_PATHS.get(name, [])
    for path in paths:
        if path.exists():
            return str(path)
    return None


def get_chrome_path() -> str | None:
    """Get Google Chrome executable path."""
    return find_app("chrome")


def get_browser_url(app_name: str) -> str | None:
    """Get the browser URL fallback for an app."""
    return BROWSER_URLS.get(app_name.lower().strip())
