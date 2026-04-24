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
- ✅ 支持最小化到系统托盘
- ✅ 可随时取消或启用自动关机

## 快速开始

### 开发环境运行

本项目使用 **uv** 作为包管理器。

```bash
# 安装依赖
uv sync

# 运行程序
uv run python src/work_time_progress.py
```

### 打包成可执行文件

```bash
# 使用打包脚本（推荐）
python build.py

# 或手动打包
uv sync --extra build
uv run pyinstaller build.spec
```

打包完成后，可执行文件位于 `dist\工作时间进度.exe`

## 安装依赖

### 使用 uv（推荐）
```bash
# 安装运行依赖
uv sync

# 安装打包依赖
uv sync --extra build
```

### 依赖说明
- **PyQt6**: GUI框架
- **pyinstaller**: 打包工具（仅打包时需要）
- **Pillow**: 图像处理（仅打包时需要）

## 使用方法

### 1. 启动程序

```bash
# 开发环境
uv run python src/work_time_progress.py

# 或直接运行打包后的exe
.\dist\工作时间进度.exe
```

### 2. 首次使用

程序首次运行时会使用默认设置：
- 上班时间：09:00
- 下班时间：18:00
- 进度条起始颜色：#0078D4（蓝色）
- 进度条结束颜色：#0d3b0a（深绿色）

### 3. 设置时间

通过系统托盘图标右键菜单，选择"设置时间"，可以修改上班和下班时间。

### 4. 功能说明

#### 进度条显示
- 屏幕顶部渐变色进度条
- 实时显示当前工作进度
- 窗口置顶，不影响其他操作

#### 系统托盘菜单
- **显示进度条/隐藏进度条**：控制进度条显示
- **设置时间**：修改上班和下班时间
- **选择颜色**：自定义进度条渐变色
  - 起始颜色：进度条左侧颜色
  - 结束颜色：进度条右侧颜色（根据进度动态计算）
- **取消关机/启用关机**：切换自动关机功能
- **退出**：关闭程序

#### 自动关机
- 到达下班时间时，程序会弹出确认对话框
- 可以选择立即关机或取消
- 如果取消，当天不再提示关机
- 第二天会自动重置关机状态
- 可以通过托盘菜单随时启用或取消自动关机功能

## 配置文件

程序会在exe同目录生成 `config.json` 配置文件：

```json
{
    "start_time": "09:00",
    "end_time": "18:00",
    "progress_color_start": "#0078D4",
    "progress_color_end": "#0d3b0a"
}
```

您也可以直接编辑此文件来修改设置。

## 打包说明

### 环境要求

本项目使用 **uv** 作为包管理器和虚拟环境工具。

### 打包步骤

#### 方法1：使用Python打包脚本（推荐）
```bash
python build.py
```

脚本会自动：
1. 检查uv环境
2. 同步项目依赖（包括打包依赖）
3. 清理旧的构建文件
4. 使用PyInstaller打包

#### 方法2：手动打包
```bash
# 1. 同步依赖（包括打包依赖）
uv sync --extra build

# 2. 打包
uv run pyinstaller build.spec
```

### 打包配置

`build.spec` 文件包含完整的打包配置：
- 单文件exe输出
- 无控制台窗口
- 包含所有必要的依赖模块（PyQt6）
- 包含图标文件

### 打包后的文件

```
dist/
└── 工作时间进度.exe    # 可执行文件（约30-40MB）
```

首次运行时会在exe同目录下自动创建 `config.json` 配置文件。

## 技术栈

- **GUI框架**: PyQt6
- **包管理**: uv
- **打包工具**: PyInstaller
- **Windows API**: ctypes (用于移除窗口圆角)

## 系统要求

### 开发环境
- Python 3.8+
- uv 包管理器
- Windows / macOS / Linux

### 打包后的exe
- Windows 10/11
- 不需要安装Python
- 不需要额外的依赖库

## 项目结构

```
WorkTime/
├── src/
│   └── work_time_progress.py  # 主程序
├── icon.ico                    # 应用图标
├── build.py                    # 打包脚本
├── build.spec                  # PyInstaller配置
├── pyproject.toml              # 项目配置和依赖
├── uv.lock                     # 依赖锁定文件
└── README.md                   # 项目说明
```

## 分发

打包完成后，只需要分发 `dist\工作时间进度.exe` 文件即可。
用户首次运行时会自动创建配置文件，无需额外配置。

## 许可证

MIT License
