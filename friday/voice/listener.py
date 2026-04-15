# voice/listener.py
import sounddevice as sd
import numpy as np
import threading
import queue
import time

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("[Friday STT] faster-whisper not available")

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5  # seconds of silence before stopping

_model = None
_model_lock = threading.Lock()


def _whisper_device_and_compute():
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def _get_model():
    global _model
    with _model_lock:
        if _model is None and WHISPER_AVAILABLE:
            device, compute_type = _whisper_device_and_compute()
            print(f"[Friday STT] Loading Whisper model (base) on {device}...")
            _model = WhisperModel("base", device="cpu", compute_type="int8")
            print(f"[Friday STT] Whisper ready ({device}).")
        return _model


def listen_once(timeout: int = 10) -> str:
    """
    Listen from mic until silence detected or timeout.
    Returns transcribed text string.
    """
    if not WHISPER_AVAILABLE:
        return input("[Friday STT not available] Type instead: ").strip()

    print("[Friday] Listening...")
    audio_queue = queue.Queue()
    frames = []
    silent_chunks = 0
    speaking_started = False
    chunks_per_second = SAMPLE_RATE // BLOCK_SIZE
    silence_chunks_needed = int(SILENCE_DURATION * chunks_per_second)

    def callback(indata, frame_count, time_info, status):
        volume = np.sqrt(np.mean(indata**2))
        audio_queue.put((indata.copy(), volume))

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=callback,
    ):
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                break
            try:
                chunk, volume = audio_queue.get(timeout=1)
                if volume > SILENCE_THRESHOLD:
                    speaking_started = True
                    silent_chunks = 0
                    frames.append(chunk)
                elif speaking_started:
                    frames.append(chunk)
                    silent_chunks += 1
                    if silent_chunks >= silence_chunks_needed:
                        break
            except queue.Empty:
                if speaking_started:
                    break

    if not frames:
        return ""

    audio_data = np.concatenate(frames, axis=0).flatten()

    try:
        model = _get_model()
        segments, _ = model.transcribe(audio_data, beam_size=5, language="en")
        text = " ".join([seg.text for seg in segments]).strip()
        print(f"[Friday STT] Heard: {text}")
        return text
    except Exception as e:
        print(f"[Friday STT] Transcription error: {e}")
        return ""


def preload():
    """Preload Whisper model on startup."""
    threading.Thread(target=_get_model, daemon=True).start()
