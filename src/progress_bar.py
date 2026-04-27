from __future__ import annotations

import ctypes

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QApplication, QWidget


class ProgressBar(QWidget):
    """屏幕顶部的渐变色进度条组件"""
    def __init__(self) -> None:
        super().__init__()
        self.progress_value: float = 0
        self.shimmer_offset: float = 0
        self.color_start = QColor("#0078D4")
        self.color_end = QColor("#00D4AA")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), 2)
        self.setFixedHeight(2)
        self.setStyleSheet("background-color: #fff;")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        try:
            hwnd = int(self.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    def set_progress(self, value: float) -> None:
        self.progress_value = value
        self.update()

    def set_colors(self, start: str, end: str) -> None:
        self.color_start = QColor(start)
        self.color_end = QColor(end)
        self.update()

    def update_shimmer(self, offset: float) -> None:
        self.shimmer_offset = offset
        self.update()

    def _interpolate_color(self, factor: float) -> QColor:
        s, e = self.color_start, self.color_end
        return QColor(
            int(s.red() + (e.red() - s.red()) * factor),
            int(s.green() + (e.green() - s.green()) * factor),
            int(s.blue() + (e.blue() - s.blue()) * factor),
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        width, height = self.width(), self.height()
        progress_width = int(width * self.progress_value / 100)

        if progress_width > 0:
            factor = self.progress_value / 100
            end_color = self._interpolate_color(factor)

            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, self.color_start)
            gradient.setColorAt(1, end_color)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillRect(0, 0, progress_width, height, gradient)

            shimmer_width = max(progress_width * 0.2, 100)
            shimmer_center = self.shimmer_offset % (progress_width + shimmer_width) - shimmer_width / 2

            shimmer_gradient = QLinearGradient(
                shimmer_center - shimmer_width / 2, 0,
                shimmer_center + shimmer_width / 2, 0,
            )
            shimmer_gradient.setColorAt(0, QColor(255, 255, 255, 0))
            shimmer_gradient.setColorAt(0.5, QColor(255, 255, 255, 180))
            shimmer_gradient.setColorAt(1, QColor(255, 255, 255, 0))

            shimmer_rect = QRect(
                int(max(0, shimmer_center - shimmer_width / 2)), 0,
                int(min(shimmer_width, progress_width - max(0, shimmer_center - shimmer_width / 2))), height,
            )
            if shimmer_rect.width() > 0:
                painter.fillRect(shimmer_rect, shimmer_gradient)

        painter.end()
