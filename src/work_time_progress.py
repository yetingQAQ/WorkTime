import json
import os
import sys
import ctypes
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu,
                              QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QMessageBox, QColorDialog)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap


class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.progress_value = 0
        self.shimmer_offset = 0
        self.color_start = QColor("#0078D4")
        self.color_end = QColor("#00D4AA")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), 2)
        self.setFixedHeight(2)
        self.setStyleSheet("background-color: #fff;")

    def showEvent(self, event):
        super().showEvent(event)
        try:
            hwnd = int(self.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass

    def set_progress(self, value):
        self.progress_value = value
        self.update()

    def set_colors(self, start, end):
        self.color_start = QColor(start)
        self.color_end = QColor(end)
        self.update()

    def update_shimmer(self, offset):
        self.shimmer_offset = offset
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        width, height = self.width(), self.height()
        progress_width = int(width * self.progress_value / 100)

        if progress_width > 0:
            factor = self.progress_value / 100
            end_color = QColor(
                int(self.color_start.red() + (self.color_end.red() - self.color_start.red()) * factor),
                int(self.color_start.green() + (self.color_end.green() - self.color_start.green()) * factor),
                int(self.color_start.blue() + (self.color_end.blue() - self.color_start.blue()) * factor)
            )

            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, self.color_start)
            gradient.setColorAt(1, end_color)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillRect(0, 0, progress_width, height, gradient)

            # 流光效果
            shimmer_width = max(progress_width * 0.2, 100)
            shimmer_center = self.shimmer_offset % (progress_width + shimmer_width) - shimmer_width / 2

            shimmer_gradient = QLinearGradient(
                shimmer_center - shimmer_width / 2, 0,
                shimmer_center + shimmer_width / 2, 0
            )
            shimmer_gradient.setColorAt(0, QColor(255, 255, 255, 0))
            shimmer_gradient.setColorAt(0.5, QColor(255, 255, 255, 180))
            shimmer_gradient.setColorAt(1, QColor(255, 255, 255, 0))

            shimmer_rect = QRect(
                int(max(0, shimmer_center - shimmer_width / 2)), 0,
                int(min(shimmer_width, progress_width - max(0, shimmer_center - shimmer_width / 2))), height
            )

            if shimmer_rect.width() > 0:
                painter.fillRect(shimmer_rect, shimmer_gradient)


class SettingsDialog(QDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("时间设置")
        self.setModal(True)

        layout = QVBoxLayout()

        for label_text, time_key in [("上班时间:", "start_time"), ("下班时间:", "end_time")]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))

            hour = QComboBox()
            hour.addItems([f"{h:02d}" for h in range(24)])
            hour.setCurrentText(config[time_key].split(':')[0])

            minute = QComboBox()
            minute.addItems([f"{m:02d}" for m in range(0, 60, 5)])
            minute.setCurrentText(config[time_key].split(':')[1])

            row.addWidget(hour)
            row.addWidget(QLabel(":"))
            row.addWidget(minute)
            layout.addLayout(row)

            setattr(self, f"{time_key.split('_')[0]}_hour", hour)
            setattr(self, f"{time_key.split('_')[0]}_minute", minute)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_times(self):
        return (
            f"{self.start_hour.currentText()}:{self.start_minute.currentText()}",
            f"{self.end_hour.currentText()}:{self.end_minute.currentText()}"
        )


class WorkTimeProgress:
    def __init__(self):
        self.app_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                                       else os.path.abspath(__file__))
        self.resource_dir = getattr(sys, '_MEIPASS', os.path.dirname(self.app_dir))
        self.config_file = os.path.join(self.app_dir, "config.json")

        self.config = self._load_config()
        self.app = QApplication(sys.argv)

        self.progress_bar = ProgressBar()
        self.progress_bar.set_colors(
            self.config['progress_color_start'],
            self.config['progress_color_end']
        )
        self.progress_bar.show()

        self.shutdown_enabled = True
        self.shutdown_cancelled = False
        self.shutdown_dialog_shown = False
        self.shimmer_offset = 0

        self._create_tray_icon()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_progress)
        self.update_timer.start(1000)

        self.shimmer_timer = QTimer()
        self.shimmer_timer.timeout.connect(self._animate_shimmer)

    def _load_config(self):
        default = {
            "start_time": "09:00",
            "end_time": "18:00",
            "progress_color_start": "#0078D4",
            "progress_color_end": "#0d3b0a"
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = {**default, **json.load(f)}
                    return config
            except:
                pass

        self._save_config(default)
        return default

    def _save_config(self, config=None):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config or self.config, f, indent=4, ensure_ascii=False)

    def _create_tray_icon(self):
        icon_path = os.path.join(self.resource_dir, 'icon.ico')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon(
            QPixmap(64, 64).copy().scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        )

        self.tray_icon = QSystemTrayIcon(icon, self.app)
        menu = QMenu()

        menu.addAction("显示进度条", self.progress_bar.show)
        menu.addAction("隐藏进度条", self.progress_bar.hide)
        menu.addSeparator()
        menu.addAction("设置时间", self._show_settings)

        color_menu = menu.addMenu("选择颜色")
        color_menu.addAction("起始颜色", lambda: self._choose_color('start'))
        color_menu.addAction("结束颜色", lambda: self._choose_color('end'))

        menu.addSeparator()
        self.shutdown_action = menu.addAction(
            "取消关机" if self.shutdown_enabled else "启用关机",
            self._toggle_shutdown
        )
        menu.addSeparator()
        menu.addAction("退出", self._quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _update_progress(self):
        now = datetime.now().time()
        start = datetime.strptime(self.config['start_time'], '%H:%M').time()
        end = datetime.strptime(self.config['end_time'], '%H:%M').time()

        to_seconds = lambda t: t.hour * 3600 + t.minute * 60 + (t.second if hasattr(t, 'second') else 0)
        current_sec, start_sec, end_sec = to_seconds(now), to_seconds(start), to_seconds(end)

        if current_sec < start_sec:
            progress = 0
            self.shutdown_cancelled = self.shutdown_dialog_shown = False
        elif current_sec >= end_sec:
            progress = 100
            if self.shutdown_enabled and not self.shutdown_cancelled and not self.shutdown_dialog_shown:
                self._shutdown_computer()
        else:
            progress = (current_sec - start_sec) / (end_sec - start_sec) * 100

        old_progress = self.progress_bar.progress_value
        self.progress_bar.set_progress(progress)

        if progress > 0 and old_progress == 0:
            self.shimmer_timer.start(30)
        elif progress == 0 and old_progress > 0:
            self.shimmer_timer.stop()
            self.shimmer_offset = 0

    def _animate_shimmer(self):
        self.shimmer_offset += 12
        self.progress_bar.update_shimmer(self.shimmer_offset)

    def _show_settings(self):
        dialog = SettingsDialog(self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config['start_time'], self.config['end_time'] = dialog.get_times()
            self._save_config()

    def _choose_color(self, color_type):
        key = f'progress_color_{"start" if color_type == "start" else "end"}'
        color = QColorDialog.getColor(
            QColor(self.config[key]),
            self.progress_bar,
            f"选择进度条{'起始' if color_type == 'start' else '结束'}颜色"
        )
        if color.isValid():
            self.config[key] = color.name()
            self._save_config()
            self.progress_bar.set_colors(
                self.config['progress_color_start'],
                self.config['progress_color_end']
            )

    def _toggle_shutdown(self):
        self.shutdown_enabled = not self.shutdown_enabled
        self.shutdown_cancelled = not self.shutdown_enabled
        self.shutdown_action.setText("取消关机" if self.shutdown_enabled else "启用关机")

    def _shutdown_computer(self):
        self.shutdown_dialog_shown = True
        reply = QMessageBox.question(
            self.progress_bar,
            "关机确认",
            "工作时间已结束，是否立即关机？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            os.system('shutdown /s /t 10' if sys.platform == 'win32' else 'shutdown -h +1')
        else:
            self.shutdown_cancelled = True
            self.shutdown_dialog_shown = False

    def _quit(self):
        self.update_timer.stop()
        self.shimmer_timer.stop()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    WorkTimeProgress().run()
