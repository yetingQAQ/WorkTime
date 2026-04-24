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
- ✅ 可自定义上班和下班时间
- ✅ 可自定义进度条渐变色
- ✅ 支持最小化到系统托盘
- ✅ 右键菜单快速访问功能
- ✅ 可随时取消或启用自动关机
- ✅ 每天自动重置关机状态

## 快速开始

### 开发环境运行

本项目使用 **uv** 作为包管理器。

```bash
# 安装依赖
uv sync

# 运行程序
uv run python work_time_progress.py
```

### 打包成可执行文件

```bash
# 使用打包脚本（推荐）
python build.py

# 或手动打包
uv sync
uv pip install pyinstaller
uv run pyinstaller build.spec
```

打包完成后，可执行文件位于 `dist\工作时间进度.exe`

## 安装依赖

### 使用 uv（推荐）
```bash
uv sync
```

### 使用 pip
```bash
pip install -r requirements.txt
```

### 依赖说明
- **pystray**: 系统托盘支持
- **Pillow**: 图像处理（用于托盘图标）
- **tkinter**: GUI界面（Python标准库）

## 使用方法

### 1. 启动程序

```bash
# 开发环境
uv run python work_time_progress.py

# 或直接运行打包后的exe
.\dist\工作时间进度.exe
```

### 2. 首次使用

程序首次运行时会使用默认设置：
- 上班时间：09:00
- 下班时间：18:00
- 进度条起始颜色：#0078D4（蓝色）
- 进度条结束颜色：#00D4AA（青色）

### 3. 设置时间

通过系统托盘图标右键菜单，选择"设置时间"，可以修改上班和下班时间。

### 4. 功能说明

#### 进度条显示
- 屏幕顶部2像素高的渐变色进度条
- 实时显示当前工作进度
- 窗口置顶，不影响其他操作

#### 系统托盘菜单
- **显示进度条/隐藏进度条**：控制进度条显示
- **设置时间**：修改上班和下班时间
- **选择颜色**：自定义进度条渐变色
  - 起始颜色：进度条左侧颜色
  - 结束颜色：进度条右侧颜色
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
    "progress_color_end": "#00D4AA"
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

#### 方法2：手动打包
```bash
# 1. 同步依赖
uv sync

# 2. 安装PyInstaller
uv pip install pyinstaller

# 3. 打包
uv run pyinstaller build.spec
```

### 打包配置

`build.spec` 文件包含完整的打包配置：
- 单文件exe输出
- 无控制台窗口
- 包含所有必要的依赖模块

### 打包后的文件

```
dist/
└── 工作时间进度.exe    # 可执行文件（约15-20MB）
```

首次运行时会在exe同目录下自动创建 `config.json` 配置文件。

## 系统要求

### 开发环境
- Python 3.8+
- uv 包管理器
- Windows / macOS / Linux

### 打包后的exe
- Windows 7 及以上
- 不需要安装Python
- 不需要额外的依赖库

## 常见问题

### 开发相关

**Q: 如何安装 uv？**
```bash
pip install uv
```

**Q: 系统托盘图标不显示？**
- 确保已安装 pystray 和 Pillow：`uv sync`
- 检查系统托盘设置是否允许显示图标

### 打包相关

**Q: 打包后运行报错？**
- 确保使用 `build.spec` 文件打包
- 检查是否有杀毒软件拦截
- 尝试以管理员权限运行

**Q: 配置文件保存失败？**
- 确保exe有写入权限
- 不要放在需要管理员权限的目录（如 C:\Program Files）

**Q: 关机命令无效？**
- Windows：确保有管理员权限
- Linux/macOS：可能需要sudo权限，建议手动关机

## 分发

打包完成后，只需要分发 `dist\工作时间进度.exe` 文件即可。
用户首次运行时会自动创建配置文件，无需额外配置。

## 许可证

MIT License
