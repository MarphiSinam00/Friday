# ui/waveform.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
import math
import random


class WaveformWidget(QWidget):
    """Animated waveform that pulses when Friday is speaking or listening."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self._active = False
        self._phase = 0.0
        self._amplitudes = [random.uniform(0.3, 1.0) for _ in range(20)]
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)
        self._color = QColor("#00d4ff")

    def set_active(self, active: bool, color: str = "#00d4ff"):
        self._active = active
        self._color = QColor(color)
        self.update()

    def _animate(self):
        if self._active:
            self._phase += 0.2
            self._amplitudes = [
                abs(math.sin(self._phase + i * 0.5)) * random.uniform(0.5, 1.0)
                for i in range(20)
            ]
        else:
            self._amplitudes = [0.05 for _ in range(20)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        mid = h // 2
        bar_width = max(2, w // 25)
        spacing = w // 20

        pen = QPen(self._color)
        pen.setWidth(bar_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for i, amp in enumerate(self._amplitudes):
            x = int(spacing * i + spacing // 2)
            bar_h = int(amp * (mid - 4))
            painter.drawLine(x, mid - bar_h, x, mid + bar_h)
