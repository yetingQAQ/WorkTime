from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Config:
    """应用配置类，管理工作时间和进度条颜色设置"""
    start_time: str = "09:00"
    end_time: str = "18:00"
    progress_color_start: str = "#0078D4"
    progress_color_end: str = "#0d3b0a"
    shimmer_speed: float = 1.0

    @staticmethod
    def load(path: Path) -> Config:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            valid = {k: v for k, v in data.items() if k in Config.__dataclass_fields__}
            return Config(**valid)
        except Exception:
            return Config()

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=4, ensure_ascii=False), encoding="utf-8")
