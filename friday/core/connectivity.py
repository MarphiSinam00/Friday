# core/connectivity.py
import socket
import threading
import time
from config.settings import PING_HOST, PING_INTERVAL_SECONDS

_is_online = False
_callbacks = []  # functions to call when mode changes
_lock = threading.Lock()


def _check_connection() -> bool:
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((PING_HOST, 53))
        return True
    except OSError:
        return False


def _monitor_loop():
    global _is_online
    while True:
        status = _check_connection()
        with _lock:
            if status != _is_online:
                _is_online = status
                mode = "ONLINE" if status else "OFFLINE"
                print(f"\n[Friday] Mode switched → {mode}")
                for cb in _callbacks:
                    try:
                        cb(status)
                    except Exception as e:
                        print(f"[Friday] Callback error: {e}")
        time.sleep(PING_INTERVAL_SECONDS)


def start_monitor():
    """Start the background connectivity watcher."""
    global _is_online
    _is_online = _check_connection()
    t = threading.Thread(target=_monitor_loop, daemon=True)
    t.start()
    mode = "ONLINE" if _is_online else "OFFLINE"
    print(f"[Friday] Connectivity monitor started — currently {mode}")


def is_online() -> bool:
    with _lock:
        return _is_online


def on_mode_change(callback):
    """Register a function to be called when online/offline status changes."""
    _callbacks.append(callback)
