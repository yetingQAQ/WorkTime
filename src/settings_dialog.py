from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

from config import Config


class SettingsDialog(QDialog):
    """时间设置对话框"""
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.setWindowTitle("时间设置")
        self.setModal(True)
        self._time_controls: dict[str, tuple[QComboBox, QComboBox]] = {}

        layout = QVBoxLayout()
        for label_text, attr in [("上班时间:", "start_time"), ("下班时间:", "end_time")]:
            h, m = getattr(config, attr).split(":")
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))

            hour = QComboBox()
            hour.addItems([f"{i:02d}" for i in range(24)])
            hour.setCurrentText(h)

            minute = QComboBox()
            minute.addItems([f"{i:02d}" for i in range(0, 60, 5)])
            minute.setCurrentText(m)

            row.addWidget(hour)
            row.addWidget(QLabel(":"))
            row.addWidget(minute)
            layout.addLayout(row)

            prefix = attr.split("_")[0]
            self._time_controls[prefix] = (hour, minute)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def get_times(self) -> tuple[str, str]:
        start_hour, start_minute = self._time_controls["start"]
        end_hour, end_minute = self._time_controls["end"]
        return (
            f"{start_hour.currentText()}:{start_minute.currentText()}",
            f"{end_hour.currentText()}:{end_minute.currentText()}",
        )
