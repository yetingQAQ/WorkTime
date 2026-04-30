from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QColorDialog, QDialog, QMenu, QMessageBox, QSystemTrayIcon,
)

from config import Config
from progress_bar import ProgressBar
from settings_dialog import SettingsDialog


class WorkTimeProgress:
    """工作时间进度条主应用程序"""
    def __init__(self) -> None:
        app_dir = Path(sys.executable if getattr(sys, "frozen", False) else __file__).parent
        self._config_path = app_dir / "config.json"
        self._resource_dir = Path(getattr(sys, "_MEIPASS", app_dir.parent))

        self.config = Config.load(self._config_path)

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        self.progress_bar = ProgressBar()
        self.progress_bar.set_colors(self.config.progress_color_start, self.config.progress_color_end)
        self.progress_bar.show()

        self.shutdown_enabled = True
        self.shutdown_cancelled = False
        self.shutdown_dialog_shown = False
        self.shimmer_offset = 0

        self._create_tray_icon()

        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_progress)
        self._update_timer.start(1000)

        self._shimmer_timer = QTimer()
        self._shimmer_timer.timeout.connect(self._animate_shimmer)

    def _create_tray_icon(self) -> None:
        icon_path = self._resource_dir / "icon.ico"
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon(
            QPixmap(64, 64).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        )

        self.tray_icon = QSystemTrayIcon(icon, self.app)
        menu = QMenu()
        menu.addAction("显示进度条", self.progress_bar.show)
        menu.addAction("隐藏进度条", self.progress_bar.hide)
        menu.addSeparator()
        menu.addAction("设置时间", self._show_settings)

        color_menu = menu.addMenu("选择颜色")
        color_menu.addAction("起始颜色", lambda: self._choose_color("start"))
        color_menu.addAction("结束颜色", lambda: self._choose_color("end"))

        speed_menu = menu.addMenu("脉冲速度")
        self._speed_actions = {}
        for label, value in [("慢", 0.5), ("正常", 1.0), ("快", 1.5), ("极快", 2.0)]:
            action = speed_menu.addAction(label, lambda v=value: self._set_shimmer_speed(v))
            action.setCheckable(True)
            action.setChecked(abs(self.config.shimmer_speed - value) < 1e-6)
            self._speed_actions[value] = action

        menu.addSeparator()
        self._shutdown_action = menu.addAction(
            "取消关机" if self.shutdown_enabled else "启用关机",
            self._toggle_shutdown,
        )
        menu.addSeparator()
        menu.addAction("退出", self._quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    @staticmethod
    def _time_to_seconds(t) -> int:
        return t.hour * 3600 + t.minute * 60 + getattr(t, "second", 0)

    def _update_progress(self) -> None:
        now = datetime.now().time()
        start = datetime.strptime(self.config.start_time, "%H:%M").time()
        end = datetime.strptime(self.config.end_time, "%H:%M").time()

        cur = self._time_to_seconds(now)
        s = self._time_to_seconds(start)
        e = self._time_to_seconds(end)

        if cur < s:
            progress = 0.0
            self.shutdown_cancelled = self.shutdown_dialog_shown = False
        elif cur >= e:
            progress = 100.0
            if self.shutdown_enabled and not self.shutdown_cancelled and not self.shutdown_dialog_shown:
                self._shutdown_computer()
        else:
            progress = (cur - s) / (e - s) * 100

        old = self.progress_bar.progress_value
        self.progress_bar.set_progress(progress)

        if progress > 0 and old == 0:
            self._shimmer_timer.start(30)
        elif progress == 0 and old > 0:
            self._shimmer_timer.stop()
            self.shimmer_offset = 0

    def _animate_shimmer(self) -> None:
        self.shimmer_offset += 12 * self.config.shimmer_speed
        self.progress_bar.update_shimmer(self.shimmer_offset)

    def _show_settings(self) -> None:
        dialog = SettingsDialog(self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config.start_time, self.config.end_time = dialog.get_times()
            self.config.save(self._config_path)

    def _choose_color(self, which: str) -> None:
        attr = f"progress_color_{which}"
        color = QColorDialog.getColor(QColor(getattr(self.config, attr)), None,
                                      f"选择进度条{'起始' if which == 'start' else '结束'}颜色")
        if color.isValid():
            setattr(self.config, attr, color.name())
            self.config.save(self._config_path)
            self.progress_bar.set_colors(self.config.progress_color_start, self.config.progress_color_end)

    def _set_shimmer_speed(self, speed: float) -> None:
        self.config.shimmer_speed = speed
        self.config.save(self._config_path)
        for value, action in self._speed_actions.items():
            action.setChecked(abs(value - speed) < 1e-6)

    def _toggle_shutdown(self) -> None:
        self.shutdown_enabled = not self.shutdown_enabled
        self.shutdown_cancelled = not self.shutdown_enabled
        self._shutdown_action.setText("取消关机" if self.shutdown_enabled else "启用关机")

    def _shutdown_computer(self) -> None:
        self.shutdown_dialog_shown = True
        reply = QMessageBox.question(
            None, "关机确认", "工作时间已结束，是否立即关机？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            os.system("shutdown /s /t 10" if sys.platform == "win32" else "shutdown -h +1")
        else:
            self.shutdown_cancelled = True
            self.shutdown_dialog_shown = False

    def _quit(self) -> None:
        self._update_timer.stop()
        self._shimmer_timer.stop()
        self.tray_icon.hide()
        self.app.quit()

    def run(self) -> None:
        sys.exit(self.app.exec())
