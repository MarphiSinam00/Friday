# ui/status_bar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet("background: #12122a; border-top: 1px solid #1e1e3a;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        self._mode_dot = QLabel("●")
        self._mode_dot.setFont(QFont("Segoe UI", 10))

        self._mode_label = QLabel("ONLINE")
        self._mode_label.setFont(QFont("Segoe UI", 9))

        self._model_label = QLabel("Brain: Gemma 3 9B")
        self._model_label.setFont(QFont("Segoe UI", 9))
        self._model_label.setStyleSheet("color: #555577;")

        self._status_label = QLabel("Ready")
        self._status_label.setFont(QFont("Segoe UI", 9))
        self._status_label.setStyleSheet("color: #555577;")

        layout.addWidget(self._mode_dot)
        layout.addWidget(self._mode_label)
        layout.addStretch()
        layout.addWidget(self._model_label)
        layout.addSpacing(20)
        layout.addWidget(self._status_label)

        self.set_online(True)

    def set_online(self, online: bool):
        if online:
            self._mode_dot.setStyleSheet("color: #00d4ff;")
            self._mode_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
            self._mode_label.setText("ONLINE")
        else:
            self._mode_dot.setStyleSheet("color: #ffa500;")
            self._mode_label.setStyleSheet("color: #ffa500; font-weight: bold;")
            self._mode_label.setText("OFFLINE")

    def set_status(self, text: str):
        self._status_label.setText(text)
