# skills/clap_detector.py
import sounddevice as sd
import numpy as np
import threading
import time

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024
CLAP_THRESHOLD = 0.3
CLAP_TIMEOUT = 1.5  # max seconds between claps
REQUIRED_CLAPS = 2

_listening = False
_callbacks = []
_last_clap_time = 0
_clap_count = 0


def on_double_clap(callback):
    """Register function to call when double clap detected."""
    _callbacks.append(callback)


def _audio_callback(indata, frames, time_info, status):
    global _last_clap_time, _clap_count
    volume = np.max(np.abs(indata))
    now = time.time()

    if volume > CLAP_THRESHOLD:
        if now - _last_clap_time > 0.1:  # debounce
            if now - _last_clap_time < CLAP_TIMEOUT:
                _clap_count += 1
            else:
                _clap_count = 1
            _last_clap_time = now

            if _clap_count >= REQUIRED_CLAPS:
                _clap_count = 0
                print("[Friday] Double clap detected!")
                for cb in _callbacks:
                    try:
                        threading.Thread(target=cb, daemon=True).start()
                    except Exception as e:
                        print(f"[Friday Clap] Callback error: {e}")


def start():
    """Start listening for claps in background."""
    global _listening
    if _listening:
        return
    _listening = True

    def _run():
        print("[Friday] Clap detector active — clap twice to wake Friday")
        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                blocksize=BLOCK_SIZE,
                dtype='float32',
                callback=_audio_callback
            ):
                while _listening:
                    time.sleep(0.1)
        except Exception as e:
            print(f"[Friday Clap] Error: {e}")

    threading.Thread(target=_run, daemon=True).start()


def stop():
    global _listening
    _listening = False
