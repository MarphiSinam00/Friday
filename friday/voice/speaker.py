import threading
import asyncio
import os
import hashlib
import soundfile as sf
import sounddevice as sd
import io
from pathlib import Path

VOICE = "en-IE-EmilyNeural"
RATE = "+10%"
PITCH = "+5Hz"
CACHE_DIR = Path(__file__).parent.parent / "data" / "voice_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_tts_engine = None


def _get_cache_path(text: str) -> Path:
    key = hashlib.md5(f"{VOICE}{RATE}{text}".encode()).hexdigest()
    return CACHE_DIR / f"{key}.wav"


def _get_pyttsx3_engine():
    global _tts_engine
    if _tts_engine is None:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        voices = _tts_engine.getProperty('voices')
        for voice in voices:
            if 'zira' in voice.name.lower():
                _tts_engine.setProperty('voice', voice.id)
                break
        _tts_engine.setProperty('rate', 175)
        _tts_engine.setProperty('volume', 0.95)
    return _tts_engine


def speak(text: str, online: bool = True):
    threading.Thread(
        target=_speak_thread,
        args=(text, online),
        daemon=True
    ).start()


def _speak_thread(text: str, online: bool):
    with _lock:
        cache_path = _get_cache_path(text)

        if cache_path.exists():
            try:
                data, samplerate = sf.read(str(cache_path))
                sd.play(data, samplerate)
                sd.wait()
                return
            except Exception as e:
                print(f"[Friday Voice] Cache play failed: {e}")
                cache_path.unlink(missing_ok=True)

        try:
            asyncio.run(_speak_edge_and_cache(text, cache_path))
            return
        except Exception as e:
            print(f"[Friday Voice] Edge TTS failed: {e}")
            _speak_and_cache_pyttsx3(text, cache_path)


async def _speak_edge_and_cache(text: str, cache_path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    if not chunks:
        raise Exception("No audio received")
    audio_bytes = b"".join(chunks)
    data, samplerate = sf.read(io.BytesIO(audio_bytes))
    try:
        sf.write(str(cache_path), data, samplerate)
    except Exception:
        pass
    sd.play(data, samplerate)
    sd.wait()


def _speak_and_cache_pyttsx3(text: str, cache_path: Path):
    try:
        import pyttsx3
        import tempfile
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 0.95)
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        engine.stop()
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            import shutil
            shutil.copy(tmp_path, str(cache_path))
            data, samplerate = sf.read(tmp_path)
            sd.play(data, samplerate)
            sd.wait()
        os.unlink(tmp_path)
    except Exception as e:
        print(f"[Friday Voice] pyttsx3 error: {e}")


def stop_speaking():
    sd.stop()
