# ui/chat_widget.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MessageBubble(QFrame):
    def __init__(self, text: str, is_friday: bool, was_online: bool = False):
        super().__init__()
        self.setObjectName("bubble")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(520)
        bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        bubble.setFont(QFont("Segoe UI", 10))
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        if is_friday:
            mode_color = "#00d4ff" if was_online else "#ffa500"
            bubble.setStyleSheet(
                f"""
                QLabel {{
                    background: #1a1a2e;
                    color: #e0e0e0;
                    border-radius: 12px;
                    border-left: 3px solid {mode_color};
                    padding: 10px 14px;
                    font-size: 10pt;
                }}
            """
            )
            layout.addWidget(bubble)
            layout.addStretch()
        else:
            bubble.setStyleSheet(
                """
                QLabel {
                    background: #0f3460;
                    color: #ffffff;
                    border-radius: 12px;
                    padding: 10px 14px;
                    font-size: 10pt;
                }
            """
            )
            layout.addStretch()
            layout.addWidget(bubble)


class ChatWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { background: #0d0d1a; border: none; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: #0d0d1a;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setSpacing(8)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.addStretch()
        self.setWidget(self._container)
        self._thinking = None

    def add_message(self, text: str, is_friday: bool, was_online: bool = False):
        bubble = MessageBubble(text, is_friday, was_online)
        self._layout.addWidget(bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def add_thinking(self):
        self.remove_thinking()
        self._thinking = MessageBubble("Friday is thinking...", True, False)
        self._layout.addWidget(self._thinking)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def remove_thinking(self):
        if self._thinking is not None:
            self._layout.removeWidget(self._thinking)
            self._thinking.deleteLater()
            self._thinking = None
