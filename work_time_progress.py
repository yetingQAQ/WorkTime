#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作时间进度条程序
在屏幕顶部显示工作进度，到下班时间自动关机
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os
from datetime import datetime, time
import threading
import sys

# Windows系统托盘支持
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("警告: 未安装pystray和Pillow库，系统托盘功能将不可用")
    print("请运行: pip install pystray Pillow")


class WorkTimeProgress:
    def __init__(self):
        # 获取exe所在目录（用于配置文件）
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            self.app_dir = os.path.dirname(sys.executable)
            # 获取资源文件目录（PyInstaller临时目录）
            self.resource_dir = sys._MEIPASS
        else:
            # 开发环境
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
            self.resource_dir = self.app_dir

        self.config_file = os.path.join(self.app_dir, "config.json")
        self.load_config()

        # 创建主窗口（进度条窗口）
        self.root = tk.Tk()
        self.root.title("工作进度")
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.attributes('-disabled', True)  # 禁用窗口交互

        # 设置任务栏图标
        self.set_taskbar_icon()

        # 设置窗口位置和大小（屏幕顶部）
        screen_width = self.root.winfo_screenwidth()
        window_height = 2
        self.root.geometry(f"{screen_width}x{window_height}+0+0")

        # 移除窗口边框
        self.root.overrideredirect(True)

        # 禁用窗口焦点
        self.root.attributes('-alpha', 0.99)  # 稍微透明以避免焦点

        # 创建Canvas作为进度条（支持渐变色）
        self.canvas = tk.Canvas(
            self.root,
            height=2,
            highlightthickness=0,
            bg='white'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 进度值
        self.progress_value = 0

        # 禁用Canvas的所有事件
        self.canvas.bind('<Button-1>', lambda e: 'break')
        self.canvas.bind('<Button-2>', lambda e: 'break')
        self.canvas.bind('<Button-3>', lambda e: 'break')
        self.canvas.bind('<Motion>', lambda e: 'break')

        # 关机标志
        self.shutdown_enabled = True
        self.shutdown_cancelled = False
        self.shutdown_dialog_shown = False

        # 系统托盘图标
        self.tray_icon = None

        # 立即创建系统托盘图标
        if TRAY_AVAILABLE:
            self.create_tray_icon()
        else:
            print("警告: 系统托盘功能不可用，请安装 pystray 和 Pillow 库")

        # 启动更新线程
        self.running = True
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "start_time": "09:00",
            "end_time": "18:00",
            "progress_color_start": "#0078D4",
            "progress_color_end": "#00D4AA"
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # 确保有颜色配置
                if 'progress_color_start' not in self.config:
                    self.config['progress_color_start'] = default_config['progress_color_start']
                if 'progress_color_end' not in self.config:
                    self.config['progress_color_end'] = default_config['progress_color_end']
                # 兼容旧版本单色配置
                if 'progress_color' in self.config and 'progress_color_start' not in self.config:
                    self.config['progress_color_start'] = self.config['progress_color']
                    self.config['progress_color_end'] = self.config['progress_color']
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        """将RGB元组转换为十六进制颜色"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def interpolate_color(self, color1, color2, factor):
        """在两个颜色之间插值"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        r = rgb1[0] + (rgb2[0] - rgb1[0]) * factor
        g = rgb1[1] + (rgb2[1] - rgb1[1]) * factor
        b = rgb1[2] + (rgb2[2] - rgb1[2]) * factor

        return self.rgb_to_hex((r, g, b))

    def draw_gradient_progress(self):
        """绘制渐变色进度条"""
        # 清除Canvas
        self.canvas.delete('all')

        # 获取Canvas尺寸
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1:  # Canvas还未完全初始化
            width = self.root.winfo_screenwidth()

        # 计算进度条宽度
        progress_width = int(width * self.progress_value / 100)

        if progress_width > 0:
            # 获取渐变色配置
            color_start = self.config.get('progress_color_start', '#0078D4')
            color_end = self.config.get('progress_color_end', '#00D4AA')

            # 绘制渐变色
            # 将进度条分成多个小段，每段颜色略有不同
            segments = min(progress_width, 100)  # 最多100个渐变段
            segment_width = progress_width / segments

            for i in range(segments):
                factor = i / max(segments - 1, 1)
                color = self.interpolate_color(color_start, color_end, factor)
                x1 = i * segment_width
                x2 = (i + 1) * segment_width
                self.canvas.create_rectangle(
                    x1, 0, x2, height,
                    fill=color,
                    outline=color
                )

    def set_taskbar_icon(self):
        """设置任务栏图标"""
        try:
            # 尝试加载icon.ico文件（从资源目录）
            icon_path = os.path.join(self.resource_dir, 'icon.ico')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                # 转换为PhotoImage
                icon_photo = tk.PhotoImage(data=self._image_to_png_data(icon_image))
                self.root.iconphoto(True, icon_photo)
            else:
                # 如果icon.ico不存在，创建一个简单的图标
                icon_image = Image.new('RGB', (64, 64), 'white')
                dc = ImageDraw.Draw(icon_image)
                # 绘制一个蓝色进度条样式的图标
                dc.rectangle([0, 0, 64, 64], fill='#0078D4')
                dc.rectangle([5, 25, 59, 39], fill='white')
                dc.rectangle([5, 25, 35, 39], fill='#00CC00')

                # 转换为PhotoImage
                icon_photo = tk.PhotoImage(data=self._image_to_png_data(icon_image))
                self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"设置任务栏图标失败: {e}")

    def _image_to_png_data(self, image):
        """将PIL Image转换为PNG数据"""
        import io
        import base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        png_data = base64.b64encode(buffer.getvalue()).decode()
        return png_data

    def update_progress(self):
        """更新进度条"""
        while self.running:
            try:
                now = datetime.now()
                current_time = now.time()

                # 解析配置的时间
                start_time = datetime.strptime(self.config['start_time'], '%H:%M').time()
                end_time = datetime.strptime(self.config['end_time'], '%H:%M').time()

                # 计算进度
                start_seconds = start_time.hour * 3600 + start_time.minute * 60
                end_seconds = end_time.hour * 3600 + end_time.minute * 60
                current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

                if current_seconds < start_seconds:
                    # 还没到上班时间
                    progress = 0
                    status = "未开始"
                    # 重置关机取消标志，为新的一天做准备
                    if self.shutdown_cancelled:
                        self.shutdown_cancelled = False
                    if self.shutdown_dialog_shown:
                        self.shutdown_dialog_shown = False
                elif current_seconds >= end_seconds:
                    # 已经到下班时间
                    progress = 100
                    status = "已完成"

                    # 检查是否需要关机
                    if self.shutdown_enabled and not self.shutdown_cancelled and not self.shutdown_dialog_shown:
                        self.shutdown_computer()
                else:
                    # 工作中
                    total_seconds = end_seconds - start_seconds
                    elapsed_seconds = current_seconds - start_seconds
                    progress = (elapsed_seconds / total_seconds) * 100
                    status = "进行中"

                # 更新UI
                self.root.after(0, self.update_ui, progress)

            except Exception as e:
                print(f"更新进度时出错: {e}")

            # 每秒更新一次
            threading.Event().wait(1)

    def update_ui(self, progress):
        """更新UI显示"""
        self.progress_value = progress
        self.draw_gradient_progress()

    def show_context_menu(self, event):
        """显示右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="设置时间", command=self.show_settings)
        menu.add_command(label="取消关机" if self.shutdown_enabled else "启用关机",
                        command=self.toggle_shutdown)
        menu.add_separator()
        menu.add_command(label="最小化到托盘", command=self.minimize_to_tray)
        menu.add_command(label="退出", command=self.quit_app)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_settings(self):
        """显示设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("时间设置")
        settings_window.attributes('-topmost', True)

        # 设置窗口大小
        window_width = 350
        window_height = 180

        # 获取屏幕尺寸
        screen_width = settings_window.winfo_screenwidth()
        screen_height = settings_window.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 生成小时和分钟选项
        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]  # 每5分钟一个选项

        # 解析当前配置的时间
        start_time_parts = self.config['start_time'].split(':')
        end_time_parts = self.config['end_time'].split(':')

        # 上班时间
        tk.Label(settings_window, text="上班时间:").grid(row=0, column=0, padx=10, pady=15, sticky='e')

        start_frame = tk.Frame(settings_window)
        start_frame.grid(row=0, column=1, padx=10, pady=15, sticky='w')

        start_hour = ttk.Combobox(start_frame, values=hours, width=5, state='readonly')
        start_hour.set(start_time_parts[0])
        start_hour.pack(side=tk.LEFT)

        tk.Label(start_frame, text=":").pack(side=tk.LEFT, padx=2)

        start_minute = ttk.Combobox(start_frame, values=minutes, width=5, state='readonly')
        start_minute.set(start_time_parts[1])
        start_minute.pack(side=tk.LEFT)

        # 下班时间
        tk.Label(settings_window, text="下班时间:").grid(row=1, column=0, padx=10, pady=15, sticky='e')

        end_frame = tk.Frame(settings_window)
        end_frame.grid(row=1, column=1, padx=10, pady=15, sticky='w')

        end_hour = ttk.Combobox(end_frame, values=hours, width=5, state='readonly')
        end_hour.set(end_time_parts[0])
        end_hour.pack(side=tk.LEFT)

        tk.Label(end_frame, text=":").pack(side=tk.LEFT, padx=2)

        end_minute = ttk.Combobox(end_frame, values=minutes, width=5, state='readonly')
        end_minute.set(end_time_parts[1])
        end_minute.pack(side=tk.LEFT)

        def save_settings():
            # 组合时间
            start_time = f"{start_hour.get()}:{start_minute.get()}"
            end_time = f"{end_hour.get()}:{end_minute.get()}"

            self.config['start_time'] = start_time
            self.config['end_time'] = end_time
            self.save_config()

            messagebox.showinfo("成功", "设置已保存！")
            settings_window.destroy()

        def cancel_settings():
            settings_window.destroy()

        # 按钮框架
        button_frame = tk.Frame(settings_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        # 让按钮框架在父容器中居中
        settings_window.grid_columnconfigure(0, weight=1)
        settings_window.grid_columnconfigure(1, weight=1)

        # 保存和取消按钮
        tk.Button(button_frame, text="保存", command=save_settings, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=cancel_settings, width=10).pack(side=tk.LEFT, padx=5)

    def toggle_shutdown(self):
        """切换关机功能"""
        self.shutdown_enabled = not self.shutdown_enabled
        self.shutdown_cancelled = not self.shutdown_enabled
        status = "已启用" if self.shutdown_enabled else "已取消"
        messagebox.showinfo("关机设置", f"自动关机功能{status}")

    def shutdown_computer(self):
        """关闭计算机"""
        # 标记对话框已显示
        self.shutdown_dialog_shown = True

        if messagebox.askyesno("关机确认", "工作时间已结束，是否立即关机？"):
            if sys.platform == 'win32':
                os.system('shutdown /s /t 10')
            elif sys.platform == 'darwin':
                os.system('sudo shutdown -h +1')
            else:
                os.system('shutdown -h +1')
        else:
            self.shutdown_cancelled = True
            self.shutdown_dialog_shown = False

    def create_tray_icon(self):
        """创建系统托盘图标"""
        if not TRAY_AVAILABLE:
            return

        # 创建托盘图标图像
        image = self.create_tray_icon_image()

        # 创建托盘菜单
        color_menu = pystray.Menu(
            pystray.MenuItem("起始颜色", self.choose_start_color),
            pystray.MenuItem("结束颜色", self.choose_end_color)
        )

        menu = pystray.Menu(
            pystray.MenuItem("显示进度条", self.show_window),
            pystray.MenuItem("隐藏进度条", self.hide_window),
            pystray.MenuItem("设置时间", self.show_settings),
            pystray.MenuItem("选择颜色", color_menu),
            pystray.MenuItem("取消关机" if self.shutdown_enabled else "启用关机",
                           self.toggle_shutdown_from_tray),
            pystray.MenuItem("退出", self.quit_app)
        )

        self.tray_icon = pystray.Icon("work_time", image, "工作进度", menu)
        # 在后台线程中运行托盘图标
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def create_tray_icon_image(self):
        """创建托盘图标图像"""
        # 尝试加载icon.ico文件（从资源目录）
        icon_path = os.path.join(self.resource_dir, 'icon.ico')
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception as e:
                print(f"加载icon.ico失败: {e}")

        # 如果icon.ico不存在或加载失败，创建默认图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)
        dc.rectangle([0, 0, width, height], fill='#0078D4')
        dc.rectangle([10, 10, width-10, height-10], fill='white')
        dc.rectangle([10, 25, width-10, 39], fill='#00CC00')
        return image

    def hide_window(self, icon=None, item=None):
        """隐藏进度条窗口"""
        self.root.withdraw()

    def show_window(self, icon=None, item=None):
        """显示进度条窗口"""
        self.root.deiconify()
        self.root.attributes('-topmost', True)

    def toggle_shutdown_from_tray(self, icon=None, item=None):
        """从托盘切换关机功能"""
        self.toggle_shutdown()
        # 重新创建菜单以更新文本
        self.update_tray_menu()

    def update_tray_menu(self):
        """更新托盘菜单"""
        if self.tray_icon:
            color_menu = pystray.Menu(
                pystray.MenuItem("起始颜色", self.choose_start_color),
                pystray.MenuItem("结束颜色", self.choose_end_color)
            )

            menu = pystray.Menu(
                pystray.MenuItem("显示进度条", self.show_window),
                pystray.MenuItem("隐藏进度条", self.hide_window),
                pystray.MenuItem("设置时间", self.show_settings),
                pystray.MenuItem("选择颜色", color_menu),
                pystray.MenuItem("取消关机" if self.shutdown_enabled else "启用关机",
                               self.toggle_shutdown_from_tray),
                pystray.MenuItem("退出", self.quit_app)
            )
            self.tray_icon.menu = menu

    def choose_start_color(self, icon=None, item=None):
        """选择进度条起始颜色"""
        current_color = self.config.get('progress_color_start', '#0078D4')

        # 创建一个临时窗口用于居中颜色选择器
        temp_window = tk.Toplevel(self.root)
        temp_window.withdraw()  # 隐藏临时窗口

        # 将临时窗口移到屏幕中央
        screen_width = temp_window.winfo_screenwidth()
        screen_height = temp_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        temp_window.geometry(f"+{x}+{y}")

        color = colorchooser.askcolor(
            color=current_color,
            title="选择进度条起始颜色",
            parent=temp_window
        )

        temp_window.destroy()

        if color and color[1]:
            self.config['progress_color_start'] = color[1]
            self.save_config()
            self.draw_gradient_progress()
            messagebox.showinfo("成功", f"起始颜色已更新为: {color[1]}")

    def choose_end_color(self, icon=None, item=None):
        """选择进度条结束颜色"""
        current_color = self.config.get('progress_color_end', '#00D4AA')

        # 创建一个临时窗口用于居中颜色选择器
        temp_window = tk.Toplevel(self.root)
        temp_window.withdraw()  # 隐藏临时窗口

        # 将临时窗口移到屏幕中央
        screen_width = temp_window.winfo_screenwidth()
        screen_height = temp_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        temp_window.geometry(f"+{x}+{y}")

        color = colorchooser.askcolor(
            color=current_color,
            title="选择进度条结束颜色",
            parent=temp_window
        )

        temp_window.destroy()

        if color and color[1]:
            self.config['progress_color_end'] = color[1]
            self.save_config()
            self.draw_gradient_progress()
            messagebox.showinfo("成功", f"结束颜色已更新为: {color[1]}")

    def on_closing(self):
        """窗口关闭事件"""
        # 不做任何事，防止意外关闭
        pass

    def quit_app(self, icon=None, item=None):
        """退出程序"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WorkTimeProgress()
    app.run()
