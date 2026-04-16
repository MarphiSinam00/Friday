import sounddevice as sd
import numpy as np
import threading
import time

SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CLAP_THRESHOLD = 0.15
CLAP_TIMEOUT = 1.2
REQUIRED_CLAPS = 2

_listening = False
_callbacks = []
_clap_times = []
_lock = threading.Lock()


def on_double_clap(callback):
    _callbacks.append(callback)


def _audio_callback(indata, frames, time_info, status):
    global _clap_times
    volume = np.max(np.abs(indata))
    now = time.time()

    if volume > CLAP_THRESHOLD:
        with _lock:
            _clap_times = [t for t in _clap_times if now - t < CLAP_TIMEOUT]
            if not _clap_times or now - _clap_times[-1] > 0.1:
                _clap_times.append(now)
                print(f"[Friday Clap] Clap detected! Count: {len(_clap_times)}")
                if len(_clap_times) >= REQUIRED_CLAPS:
                    _clap_times = []
                    print("[Friday] Double clap detected!")
                    for cb in _callbacks:
                        try:
                            threading.Thread(target=cb, daemon=True).start()
                        except Exception as e:
                            print(f"[Friday Clap] Error: {e}")


def start():
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
                dtype="float32",
                callback=_audio_callback
            ):
                while _listening:
                    time.sleep(0.1)
        except Exception as e:
            print(f"[Friday Clap] Stream error: {e}")

    threading.Thread(target=_run, daemon=True).start()


def stop():
    global _listening
    _listening = False
