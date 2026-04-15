# core/offline_llm.py
import ollama
from config.settings import OFFLINE_MODEL, OLLAMA_HOST


def check_model_available() -> bool:
    """Check if Gemma 3 9B is pulled in Ollama."""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        models = client.list()
        names = [m.model for m in models.models]
        return any(OFFLINE_MODEL in name for name in names)
    except Exception as e:
        print(f"[Friday] Ollama check failed: {e}")
        return False


def pull_model_if_needed():
    import subprocess
    import time
    try:
        if check_model_available():
            print(f"[Friday] {OFFLINE_MODEL} already available.")
            return
    except Exception:
        pass
    
    print("[Friday] Starting Ollama...")
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
    
    try:
        if check_model_available():
            print(f"[Friday] {OFFLINE_MODEL} ready.")
            return
    except Exception:
        pass
    
    try:
        print(f"[Friday] Pulling {OFFLINE_MODEL}...")
        client = ollama.Client(host=OLLAMA_HOST)
        client.pull(OFFLINE_MODEL)
        print(f"[Friday] {OFFLINE_MODEL} ready.")
    except Exception as e:
        print(f"[Friday] Could not pull model (offline?): {e}")
        print(f"[Friday] Will try to use existing model...")


def chat(messages: list[dict], system_prompt: str) -> str:
    """Send messages to local Ollama LLM and return response."""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat(
            model=OFFLINE_MODEL,
            messages=full_messages,
        )
        return response.message.content.strip()
    except Exception as e:
        return f"[Friday offline error] {e}"
