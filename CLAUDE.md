# CLAUDE.md — Friday AI Assistant
# Complete Project Documentation for AI Understanding
 
---
 
## PROJECT OVERVIEW
 
**Friday** is a JARVIS-inspired personal AI assistant built for Windows 11.
It is a hybrid system that runs fully offline using a local LLM and
automatically upgrades to enhanced online intelligence when internet
is available. Named after the MCU AI assistant from Iron Man.
 
**Owner:** Marphi Sinam (goes by Mark, addressed as Sir)
**Machine:** Lenovo LOQ 15ARP9
**OS:** Windows 11 Home (25H2)
**CPU:** AMD Ryzen 7 7435HS (3.10 GHz, 8-core)
**GPU:** NVIDIA GeForce RTX 4060 Laptop (8 GB VRAM)
**RAM:** 24 GB DDR5
**Python:** 3.13
**Project Path:** C:\Users\Marphi Sinam\OneDrive\Desktop\Friday\friday
 
---
 
## CORE CONCEPT
 
Friday operates in two modes that switch automatically:
 
```
OFFLINE MODE
  Brain    → Gemma 3 9B Q4 (local, via Ollama, runs on RTX 4060 GPU)
  Voice    → Edge TTS en-IE-EmilyNeural (cached) → pyttsx3 fallback
  Features → All core features work without internet
 
ONLINE MODE
  Brain    → Gemma 3 9B local + Claude API for deep tasks
  Voice    → Edge TTS en-IE-EmilyNeural (live streaming)
  Features → Web search, real-time info, enhanced intelligence
```
 
Connectivity is checked every 30 seconds via socket ping to 8.8.8.8.
When mode changes, Friday notifies Sir and switches brain automatically.
 
---
 
## PERSONALITY & IDENTITY
 
- Name: Friday
- Voice: Irish female, calm and professional (MCU Friday inspired)
- Voice engine: Microsoft Edge TTS — en-IE-EmilyNeural
- Rate: +10%, Pitch: +5Hz (slightly crisp and natural)
- Always addresses user as Sir
- Only uses the name Mark when Sir specifically asks about his name
- Short responses — maximum 2-3 sentences unless asked for detail
- Never uses asterisks, markdown, or special symbols in speech
- Witty, warm, proactive, emotionally intelligent
- Never reveals she is Gemma, Google, or any AI model
---
 
## FEATURES
 
### Phase 1 — Brain & Memory (COMPLETE)
- Local LLM via Ollama (Gemma 3 latest = 9B model)
- Automatic online/offline detection and switching
- SQLite conversation history via SQLAlchemy ORM
- User profile memory (name, preferences)
- Real-time date and time injection into every prompt
- Claude API integration for online deep reasoning
### Phase 2 — Voice & UI (COMPLETE)
- PyQt6 dark JARVIS-style window
- Chat bubbles (blue border = online, orange = offline)
- Animated waveform visualizer
- Online/Offline status indicator
- Edge TTS female Irish voice (Emily)
- Voice caching system (responses saved as WAV locally)
- Mic button for voice input
- System tray support (minimizes, stays running)
- faster-whisper STT on CPU (GPU not supported on Python 3.13 yet)
- Auto-listen mode after every response
### Phase 3 — Skills & OS Control (COMPLETE)
- Smart app detection (checks local install first, Chrome fallback)
- Open Spotify, YouTube, Netflix, WhatsApp by voice or text
- Bored mode — jokes, fun facts, opens entertainment automatically
- Reminder system — "remind me in X minutes to do Y"
- Screenshot capture (saves to Desktop/Friday_Screenshots)
- File reader (PDF, DOCX, TXT)
- Screen vision (screenshot + describe)
- Double clap detection to wake Friday
- Always-on voice listening mode
### Phase 4 — Hybrid Intelligence (PLANNED)
- Claude API as online brain for deep tasks
- Web search and real-time summarization
- ChromaDB vector memory for semantic recall
- Proactive suggestions based on context
- Complete long-term memory system
---
 
## FOLDER STRUCTURE
 
```
Friday/
└── friday/                          ← Main project root (run from here)
    ├── main.py                      ← Entry point
    ├── requirements.txt             ← Python dependencies
    │
    ├── config/
    │   ├── settings.py              ← All configuration and personality
    │   └── .env                     ← API keys (never commit)
    │
    ├── core/
    │   ├── brain.py                 ← Main router (skills + LLM)
    │   ├── offline_llm.py           ← Gemma 3 via Ollama
    │   ├── connectivity.py          ← Internet monitor (background thread)
    │   └── context.py               ← Builds system prompt with time + memory
    │
    ├── memory/
    │   ├── database.py              ← SQLAlchemy models + SQLite init
    │   ├── history.py               ← Read/write conversation history
    │   └── user_profile.py          ← Key-value store for user preferences
    │
    ├── voice/
    │   ├── listener.py              ← faster-whisper STT (CPU mode)
    │   ├── speaker.py               ← Edge TTS + cache + pyttsx3 fallback
    │   └── wake_word.py             ← Disabled (replaced by clap detector)
    │
    ├── ui/
    │   ├── main_window.py           ← Main PyQt6 window + all UI logic
    │   ├── chat_widget.py           ← Message bubble scroll area
    │   ├── waveform.py              ← Animated waveform widget
    │   └── status_bar.py            ← Online/offline + status indicator
    │
    ├── skills/
    │   ├── os_control.py            ← Open apps, URLs, files, screenshot
    │   ├── app_finder.py            ← Detect locally installed apps
    │   ├── bored_mode.py            ← Entertainment responses + actions
    │   ├── scheduler.py             ← Reminder and alarm system
    │   ├── clap_detector.py         ← Double clap wake detection
    │   ├── screen_vision.py         ← Screenshot capture + description
    │   └── file_reader.py           ← Read PDF, DOCX, TXT files
    │
    ├── assets/                      ← Icons and images (future)
    │
    └── data/
        ├── friday.db                ← SQLite database (auto-created)
        └── voice_cache/             ← Cached Edge TTS audio files (WAV)
```
 
---
 
## FILE EXPLANATIONS
 
### main.py
Entry point. Runs in order:
1. Initialize SQLite database
2. Start connectivity monitor (background thread)
3. Check Ollama model availability
4. Preload Whisper STT model in background
5. Launch PyQt6 application
6. Show MainWindow
### config/settings.py
Central configuration. Contains:
- USER_NAME = "Sir" (how Friday addresses the user)
- FRIDAY_PERSONALITY = full system prompt string
- OFFLINE_MODEL = "gemma3:latest"
- OLLAMA_HOST = "http://localhost:11434"
- DATABASE_URL = SQLite path
- PING_HOST and PING_INTERVAL_SECONDS for connectivity
### core/brain.py
The most important file. Does:
1. Detects if input matches a skill trigger (open spotify, bored, remind me etc)
2. If skill matched → executes skill → returns response
3. If no skill → routes to online or offline LLM
4. Online: tries Claude API first, falls back to Gemma if no API key
5. Offline: uses Gemma 3 directly
6. Extracts and saves user name from conversation if mentioned
### core/connectivity.py
Background thread that:
- Pings 8.8.8.8:53 via socket every 30 seconds
- Sets global _is_online flag
- Fires registered callbacks when mode changes
- UI updates online/offline indicator via Qt signal
### core/context.py
Builds the system prompt for every LLM call:
- Injects current date and time (so Friday always knows the time)
- Adds online/offline mode instruction
- Appends user profile data (name, preferences)
- Combines with FRIDAY_PERSONALITY
### core/offline_llm.py
Wraps Ollama Python client:
- check_model_available() — lists Ollama models
- pull_model_if_needed() — starts Ollama serve if needed, pulls model
- chat() — sends messages to Gemma 3 and returns response string
### memory/database.py
SQLAlchemy setup with two tables:
- Conversation: stores all messages with role, content, session_id, timestamp, was_online
- UserProfile: key-value store for persistent user data
- init_db() creates tables on first run
### memory/history.py
- new_session_id() — UUID for each conversation session
- save_message() — writes to Conversation table
- get_recent_history() — returns last N messages as list of dicts
### memory/user_profile.py
- set_profile(key, value) — upserts a user preference
- get_profile(key) — retrieves a preference
- get_all_profile() — returns all preferences as dict
### voice/speaker.py
TTS pipeline with caching:
1. Hash the text + voice name → cache key
2. Check if WAV cache file exists → play it directly (same voice online/offline)
3. If not cached and online → call Edge TTS → save to cache → play
4. If Edge TTS fails → pyttsx3 fallback (Microsoft Zira)
- Voice: en-IE-EmilyNeural (Irish female, MCU Friday inspired)
- Rate: +10%, Pitch: +5Hz
### voice/listener.py
- Loads faster-whisper "base" model on CPU (int8 compute)
- Records audio until silence detected (1.5 seconds of silence)
- Transcribes using Whisper and returns text string
- NOTE: GPU not used because PyTorch does not support Python 3.13 yet
- Will switch to GPU when PyTorch 3.13 support releases
### voice/wake_word.py
Currently disabled (stub functions only).
Was causing Windows fatal exception (access violation) due to
conflict between sounddevice recording and Whisper model loading
in simultaneous background threads.
Will be properly rebuilt in Phase 4.
 
### ui/main_window.py
Main PyQt6 window. Key methods:
- _show_welcome() — displays and speaks welcome message
- _on_send() — handles text input from chat box
- _on_mic_clicked() — starts voice listening thread
- _on_voice_input() — receives transcribed text, processes it
- _auto_listen() — restarts mic automatically (always-on voice mode)
- _process_input() — saves to history, starts ThinkThread
- _on_response() — receives LLM response, shows bubble, speaks
- _on_double_clap() — shows window and activates mic on clap
- _on_mode_change_ui() — updates UI when online/offline changes
- closeEvent() — minimizes to tray instead of closing
### ui/chat_widget.py
Scrollable chat area with MessageBubble widgets:
- Friday messages: dark background, blue border (online) or orange (offline)
- User messages: slightly lighter background, right-aligned
### ui/waveform.py
Animated waveform using QPainter:
- Idle: flat low amplitude bars
- Active: animated sine-wave bars
- Color: cyan (#00d4ff) for speaking, purple (#7f77dd) for thinking
### ui/status_bar.py
Bottom bar showing:
- Colored dot + ONLINE/OFFLINE text
- Brain model name (Gemma 3 9B)
- Current status (Ready, Thinking, Listening)
### skills/os_control.py
Smart app opener:
1. Check APP_PATHS for local executable
2. Try Windows shell startfile
3. Fall back to Chrome browser URL
4. Last resort: Google search in Chrome
Also handles: open_youtube(query), open_spotify(),
open_whatsapp(), open_netflix(), take_screenshot(),
open_file(), open_folder(), run_command()
### skills/app_finder.py
Dictionary of known app paths for:
Spotify, WhatsApp, Chrome, Discord, Steam,
VS Code, Notepad, Calculator, VLC
Also stores browser URL fallbacks for web apps.
 
### skills/bored_mode.py
When Sir says he is bored:
- Randomly picks: joke + fun fact, open Spotify,
  open YouTube, open Netflix + fun fact
- Returns (response_text, action_function)
- Brain executes the action after speaking
### skills/scheduler.py
Background reminder system:
- add_reminder(message, minutes, callback)
- add_reminder_at_time(message, hour, minute, callback)
- parse_reminder(text) — natural language parser
- Background thread checks every 10 seconds
### skills/clap_detector.py
Listens to microphone continuously in background:
- Detects audio spikes above threshold (0.15)
- Tracks clap timestamps within 1.2 second window
- Two claps within window = double clap detected
- Fires registered callbacks in separate threads
### skills/file_reader.py
- read_pdf() — PyMuPDF text extraction (first 3000 chars)
- read_docx() — python-docx paragraph extraction
- read_txt() — plain text reading
- read_file() — auto-detects by file extension
### skills/screen_vision.py
- capture_and_describe() — takes screenshot, saves to Desktop/Friday_Screenshots
- get_screen_context() — returns screen resolution info
---
 
## EXECUTION FLOW
 
### Startup Flow
```
python main.py
    → init_db() — create SQLite tables
    → start_monitor() — background internet checker
    → pull_model_if_needed() — ensure Gemma is available
    → preload_whisper() — load STT model in background
    → QApplication() — start Qt event loop
    → MainWindow() — create UI
        → new_session_id()
        → start_clap_detector()
        → start_scheduler()
        → show_welcome() after 500ms
        → auto_listen() after 3000ms
    → app.exec() — run event loop forever
```
 
### Message Processing Flow
```
User types or speaks
    → _process_input(text)
    → save_message(session, "user", text)
    → get_recent_history(session, limit=20)
    → ThinkThread.start()
        → think(messages)
            → detect_skill(text)
                → if skill found → handle_skill() → return response
                → if no skill → route to LLM
            → build_system_prompt()
                → inject date, time, mode, user profile
            → online? → _online_think() → Claude API or Gemma
            → offline? → offline_chat() → Gemma 3
            → _check_and_save_name()
    → _on_response(response, was_online)
        → chat.remove_thinking()
        → chat.add_message(response, bubble)
        → save_message(session, "assistant", response)
        → _speak(response)
            → speaker.speak(text, online)
                → check cache → play if found
                → Edge TTS → save cache → play
                → pyttsx3 fallback if needed
        → auto_listen() — restart mic
```
 
### Voice Flow
```
Mic button clicked OR double clap detected
    → ListenThread.start()
        → listen_once(timeout=12)
            → sounddevice records until silence
            → WhisperModel.transcribe()
            → return text
    → _on_voice_input(text)
        → _process_input(text)
        → auto_listen() after 2000ms (always-on loop)
```
 
---
 
## DEPENDENCIES
 
### Python Packages
```
ollama==0.6.1          ← Ollama Python client
sqlalchemy==2.0.49     ← Database ORM
python-dotenv==1.2.1   ← .env file loading
colorama==0.4.6        ← Terminal colors (Phase 1)
httpx==0.27.2          ← HTTP client
anthropic              ← Claude API client
PyQt6==6.10.2          ← Desktop UI framework
faster-whisper==1.2.1  ← Speech-to-text (Whisper)
sounddevice==0.5.5     ← Microphone input + audio output
numpy==2.3.3           ← Audio processing
scipy==1.16.2          ← Signal processing
soundfile==0.13.1      ← Audio file read/write
kokoro-onnx            ← TTS (installed but replaced by Edge TTS)
pyttsx3==2.98          ← Offline TTS fallback
edge-tts               ← Microsoft Neural TTS (primary voice)
pymupdf                ← PDF reading
python-docx            ← Word document reading
pillow                 ← Screenshot capture
spacy                  ← NLP (kokoro dependency)
en-core-web-md         ← spaCy English model
loguru                 ← Logging (kokoro dependency)
```
 
### External Services
```
Ollama (local server)     ← http://localhost:11434
  Model: gemma3:latest    ← 3.3 GB, Gemma 3 9B Q4
Edge TTS                  ← Microsoft Neural voice API (online)
Claude API                ← Anthropic (optional, online deep reasoning)
```
 
### System Requirements
```
Windows 11
NVIDIA GeForce RTX 4060 (8 GB VRAM) — for Gemma brain
24 GB RAM
Ollama installed and running
Python 3.13
Built-in or external microphone
```
 
---
 
## KNOWN ISSUES & NOTES FOR AI
 
### PyTorch / Python 3.13
PyTorch does not officially support Python 3.13 yet.
This means faster-whisper cannot use CUDA GPU acceleration.
Current workaround: run Whisper on CPU with int8 compute type.
When PyTorch releases 3.13 support, change in voice/listener.py:
  device="cpu", compute_type="int8"
to:
  device="cuda", compute_type="float16"
Same change needed in voice/wake_word.py when re-enabled.
 
### Wake Word
The wake word system (voice/wake_word.py) is currently disabled.
It caused a Windows fatal exception (access violation) because
sounddevice recording and Whisper model initialization conflicted
in simultaneous background threads.
Currently replaced by double clap detection (skills/clap_detector.py).
Will be rebuilt properly in Phase 4 using a lightweight dedicated
wake word library that does not conflict with sounddevice.
 
### Voice Caching
Edge TTS responses are cached as WAV files in data/voice_cache/.
Cache key = MD5 hash of (voice_name + rate + text).
Cached responses play instantly and work offline.
New responses generated offline fall back to pyttsx3 (Microsoft Zira).
This means first-time offline responses sound different.
Full solution in Phase 4: pre-cache common phrases on startup.
 
### Ollama Must Be Running
Friday requires Ollama to be running before startup.
If Ollama is not running, brain.py will attempt to start it
via subprocess but this may fail if Ollama is not in PATH.
Permanent fix: add Ollama to Windows startup applications.
 
### Model Name
User pulled model with: ollama pull gemma3
Ollama saved it as: gemma3:latest
Settings use: OFFLINE_MODEL = "gemma3:latest"
This is the Gemma 3 9B model (3.3 GB) — confirmed by file size.
 
### Database Location
SQLite database: friday/data/friday.db
Voice cache: friday/data/voice_cache/
Screenshots: Desktop/Friday_Screenshots/
All paths are created automatically on first run.
 
---
 
## PHASES SUMMARY
 
| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Complete | Brain, memory, online/offline switching |
| Phase 2 | Complete | PyQt6 UI, voice input/output, Emily voice |
| Phase 3 | Complete | Skills, OS control, clap detector, reminders |
| Phase 4 | Planned | Claude API brain, web search, ChromaDB memory |
 
---
 
## HOW TO RUN
 
```bash
# 1. Make sure Ollama is running (check system tray)
# 2. Navigate to project
cd "C:\Users\Marphi Sinam\OneDrive\Desktop\Friday\friday"
# 3. Run Friday
python main.py
```
 
## HOW TO INTERACT WITH FRIDAY
 
Text: Type in the chat box and press Enter
Voice: Click the mic button and speak
Clap: Clap twice to activate mic automatically
Tray: Close window to minimize to system tray
 
## EXAMPLE COMMANDS
 
```
open spotify
open youtube lofi music
i am bored
remind me in 10 minutes to drink water
take a screenshot
what time is it
what is my name
open chrome
open whatsapp
```
 
---
 
## FUTURE PLANS (Phase 4)
 
- ChromaDB vector memory for semantic long-term recall
- Web search with real-time summarization
- Claude API as primary online brain
- Pre-cache common phrases for consistent offline voice
- Rebuild wake word with dedicated lightweight library
- Switch Whisper to GPU when PyTorch supports Python 3.13
- Add more skills: email, calendar, weather, news briefing
- Morning briefing mode — Friday summarizes your day on startup
- Screen monitoring — Friday watches what you work on and suggests
---
 
*Generated for Friday AI Assistant — Version 1.0 Phase 3*
*Owner: Marphi Sinam | Built with Claude (Anthropic)*
