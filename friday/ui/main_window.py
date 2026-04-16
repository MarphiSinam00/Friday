# ui/main_window.py
import threading
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QSystemTrayIcon,
    QMenu,
    QApplication,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ui.chat_widget import ChatWidget
from ui.waveform import WaveformWidget
from ui.status_bar import StatusBar
from core.brain import think
from core.connectivity import is_online, on_mode_change
from memory.history import new_session_id, save_message, get_recent_history
from config.settings import FRIDAY_NAME, USER_NAME


class ThinkThread(QThread):
    """Background thread so UI doesn't freeze while Friday thinks."""

    response_ready = pyqtSignal(str, bool)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        response, was_online = think(self.messages)
        self.response_ready.emit(response, was_online)


class ListenThread(QThread):
    """Background thread for voice listening."""

    text_ready = pyqtSignal(str)

    def run(self):
        from voice.listener import listen_once

        text = listen_once(timeout=12)
        self.text_ready.emit(text)


class SpeakThread(QThread):
    """Play TTS off the UI thread; signal when playback is done."""

    finished = pyqtSignal()

    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def run(self):
        from voice.speaker import speak_blocking

        speak_blocking(self._text)
        self.finished.emit()


class MainWindow(QMainWindow):
    mode_changed = pyqtSignal(bool)
    wake_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.session_id = new_session_id()
        self.tray = None
        self._speak_generation = 0
        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._connect_signals()
        self._start_wake_word()

        # Start clap detector
        self._start_clap_detector()

        # Start reminder scheduler
        from skills.scheduler import start as start_scheduler
        start_scheduler()

        on_mode_change(self._on_mode_change_bg)

        QTimer.singleShot(500, self._show_welcome)

    def _setup_window(self):
        self.setWindowTitle(f"{FRIDAY_NAME} — Personal AI Assistant")
        self.setMinimumSize(800, 600)
        self.resize(900, 680)
        self.setStyleSheet(
            """
            QMainWindow { background: #0d0d1a; }
            QWidget { background: #0d0d1a; color: #e0e0e0; }
            QLineEdit {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QLineEdit:focus { border: 1px solid #00d4ff; }
            QPushButton {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 20px;
                padding: 8px 18px;
                font-size: 10pt;
            }
            QPushButton:hover { background: #2a2a4a; border-color: #00d4ff; }
            QPushButton:pressed { background: #00d4ff; color: #000000; }
            QPushButton#mic_btn {
                background: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 20px;
                font-size: 14pt;
                padding: 6px 14px;
            }
            QPushButton#mic_btn:hover { border-color: #00d4ff; }
            QPushButton#mic_btn.active {
                background: #003344;
                border-color: #00d4ff;
            }
        """
        )

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #12122a; border-bottom: 1px solid #1e1e3a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel(f"✦ {FRIDAY_NAME.upper()}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00d4ff; letter-spacing: 3px;")

        self.header_status = QLabel("Personal AI Assistant")
        self.header_status.setFont(QFont("Segoe UI", 9))
        self.header_status.setStyleSheet("color: #555577;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.header_status)
        root.addWidget(header)

        self.chat = ChatWidget()
        root.addWidget(self.chat, stretch=1)

        self.waveform = WaveformWidget()
        root.addWidget(self.waveform)

        input_area = QWidget()
        input_area.setFixedHeight(64)
        input_area.setStyleSheet("background: #12122a; border-top: 1px solid #1e1e3a;")
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(16, 10, 16, 10)
        input_layout.setSpacing(10)

        self.mic_btn = QPushButton("🎙")
        self.mic_btn.setObjectName("mic_btn")
        self.mic_btn.setFixedSize(44, 44)
        self.mic_btn.setToolTip("Hold to speak to Friday")
        self.mic_btn.clicked.connect(self._on_mic_clicked)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f"Message {FRIDAY_NAME}...")
        self.input_field.returnPressed.connect(self._on_send)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(80)
        self.send_btn.clicked.connect(self._on_send)

        input_layout.addWidget(self.mic_btn)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        root.addWidget(input_area)

        self.status_bar = StatusBar()
        self.status_bar.set_online(is_online())
        root.addWidget(self.status_bar)

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Friday")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self._quit)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def _connect_signals(self):
        self.mode_changed.connect(self._on_mode_change_ui)
        self.wake_detected.connect(self._on_wake_word_ui)

    def _start_wake_word(self):
        pass

    def _start_clap_detector(self):
        try:
            from skills.clap_detector import start, on_double_clap
            on_double_clap(self._on_double_clap)
            start()
        except Exception as e:
            print(f"[Friday] Clap detector not started: {e}")

    def _on_double_clap(self):
        """Called when double clap detected."""
        self.show()
        self.raise_()
        self.activateWindow()
        self._on_mic_clicked()

    def _show_welcome(self):
        try:
            online = is_online()
            mode = "online" if online else "offline"
            msg = (f"Good day, Sir. I am Friday, your personal AI assistant. "
                   f"All systems are online and fully operational. "
                   f"How may I assist you today?")
            self.chat.add_message(msg, is_friday=True, was_online=online)
            QTimer.singleShot(500, lambda: self._speak(msg))
            QTimer.singleShot(3000, self._auto_listen)
        except Exception as e:
            print(f"[Friday] Welcome error: {e}")

    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        self._process_input(text)

    def _on_mic_clicked(self):
        self.mic_btn.setEnabled(False)
        self.status_bar.set_status("Listening...")
        self.waveform.set_active(True, "#00d4ff")
        self._listen_thread = ListenThread()
        self._listen_thread.text_ready.connect(self._on_voice_input)
        self._listen_thread.start()

    def _on_voice_input(self, text: str):
        self.mic_btn.setEnabled(True)
        self.waveform.set_active(False)
        self.status_bar.set_status("Ready")
        if text:
            self._process_input(text)
            QTimer.singleShot(2000, self._auto_listen)
        else:
            self.status_bar.set_status("Didn't catch that — listening again...")
            QTimer.singleShot(500, self._auto_listen)

    def _auto_listen(self):
        if self.isVisible() and self.mic_btn.isEnabled():
            self._on_mic_clicked()

    def _on_wake_word_ui(self):
        self.show()
        self.raise_()
        self.activateWindow()
        if not self.mic_btn.isEnabled():
            return
        self._on_mic_clicked()

    def _process_input(self, text: str):
        online = is_online()
        self.chat.add_message(text, is_friday=False)
        save_message(self.session_id, "user", text, was_online=online)

        self.chat.add_thinking()
        self.status_bar.set_status("Thinking...")
        self.waveform.set_active(True, "#7f77dd")
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        history = get_recent_history(self.session_id, limit=20)
        self._think_thread = ThinkThread(history)
        self._think_thread.response_ready.connect(self._on_response)
        self._think_thread.start()

    def _on_response(self, response: str, was_online: bool):
        self.chat.remove_thinking()
        self.chat.add_message(response, is_friday=True, was_online=was_online)
        save_message(self.session_id, "assistant", response, was_online=was_online)

        self.waveform.set_active(False)
        self.status_bar.set_status("Ready")
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        QTimer.singleShot(100, lambda: self._speak(response))

    def _speak(self, text: str):
        try:
            online = is_online()
            import threading
            from voice.speaker import speak
            t = threading.Thread(target=speak, args=(text, online), daemon=True)
            t.start()
        except Exception as e:
            print(f"[Friday Voice] Speak error: {e}")

    def _on_mode_change_bg(self, online: bool):
        self.mode_changed.emit(online)

    def _on_mode_change_ui(self, online: bool):
        self.status_bar.set_online(online)
        mode = "online" if online else "offline"
        msg = f"I've switched to {mode} mode. " + (
            "Web access and enhanced intelligence are now available."
            if online
            else "I'm running on local intelligence — all core features remain available."
        )
        self.chat.add_message(msg, is_friday=True, was_online=online)
        self._speak(msg)

    def _quit(self):
        from voice.wake_word import stop

        stop()
        QApplication.quit()

    def closeEvent(self, event):
        from voice.wake_word import stop

        if self.tray is not None:
            event.ignore()
            self.hide()
            self.tray.showMessage(
                FRIDAY_NAME,
                f"{FRIDAY_NAME} is still running in the background.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            stop()
            event.accept()
