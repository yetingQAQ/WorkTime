<p align="center">
  <img src="icon.ico" alt="工作时间进度条" width="128" height="128">
</p>

<p align="center">
  <em>使用Claude Sonnet 4.5设计并实现</em>
</p>

一个在屏幕顶部显示工作进度的Python程序，根据设置的上班和下班时间自动计算进度，并在下班时间到达时提示关机。

## 功能特点

- ✅ 在屏幕最顶部显示渐变色进度条
- ✅ 根据上班时间和下班时间自动计算工作进度
- ✅ 到达下班时间时自动提示关机
- ✅ 可自定义进度条渐变色（起始色和结束色）
- ✅ 可调节脉冲流光速度（慢 / 正常 / 快 / 极快）
- ✅ 支持最小化到系统托盘
- ✅ 可随时取消或启用自动关机

## 快速开始

### 开发环境运行

本项目使用 **uv** 作为包管理器。

```bash
# 安装依赖
uv sync

# 运行程序
uv run python src/app.py
```

### 打包成可执行文件

```bash
# 兼容性好，稳定性高，适合大多数场景（推荐）
python build.py --mode safe

# 兼容性稍差，但体积较小（体积优先）
python build.py --mode aggressive
```

打包完成后，默认可执行文件位于 `dist\工作时间进度.exe`
使用 `--mode aggressive` 时，输出位于 `dist_aggressive\*.exe`。

## 配置文件

程序会在exe同目录生成 `config.json` 配置文件：

```json
{
    "start_time": "09:00",
    "end_time": "18:00",
    "progress_color_start": "#0078D4",
    "progress_color_end": "#0d3b0a",
    "shimmer_speed": 1.0
}
```

## 技术栈

- **Python版本**: Python 3.8+
- **GUI框架**: PyQt6
- **包管理**: uv
- **打包工具**: PyInstaller
- **Windows API**: ctypes (用于移除窗口圆角)

## 项目结构

```
WorkTime/
├── src/
│   ├── app.py                  # 程序入口
│   ├── config.py               # 配置管理
│   ├── progress_bar.py         # 进度条组件
│   ├── settings_dialog.py      # 设置对话框
│   └── work_time_progress.py   # 主应用程序
├── icon.ico                    # 应用图标
├── build.py                    # 打包脚本
├── build.spec                  # PyInstaller配置
├── pyproject.toml              # 项目配置和依赖
├── uv.lock                     # 依赖锁定文件
└── README.md                   # 项目说明
```

## 许可证

MIT License
