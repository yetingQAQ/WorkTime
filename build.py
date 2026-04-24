#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 适配uv虚拟环境
"""
import os
import sys
import shutil
import subprocess

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    return True

def main():
    print("=" * 50)
    print("工作时间进度条 - 打包脚本 (uv环境)")
    print("=" * 50)

    # 检查uv
    print("\n[1/5] 检查uv环境...")
    result = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("错误: 未检测到uv，请先安装uv")
        print("安装命令: pip install uv")
        input("\n按回车键退出...")
        return
    print(f"uv版本: {result.stdout.strip()}")

    # 同步依赖
    print("\n[2/5] 同步项目依赖...")
    if not run_command("uv sync --extra build", "同步依赖"):
        print("\n打包失败: 无法同步依赖")
        input("\n按回车键退出...")
        return

    # 打包不再需要单独安装PyInstaller，已包含在build依赖中
    print("\n[3/5] 准备打包环境...")
    print("PyInstaller和Pillow已通过uv sync安装")

    # 清理旧文件
    print("\n[4/5] 清理旧的构建文件...")
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("已清理 build 目录")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("已清理 dist 目录")
    if os.path.exists("工作时间进度.spec"):
        os.remove("工作时间进度.spec")
        print("已删除旧的spec文件")

    # 打包
    print("\n[5/5] 开始打包...")
    print("这可能需要几分钟，请耐心等待...\n")

    # 使用uv run来执行pyinstaller
    result = subprocess.run("uv run pyinstaller build.spec", shell=True)

    # 检查结果
    print("\n" + "=" * 50)
    if result.returncode == 0 and os.path.exists("dist/工作时间进度.exe"):
        print("✓ 打包成功！")
        print("=" * 50)
        print(f"\n可执行文件位置: {os.path.abspath('dist/工作时间进度.exe')}")
        print("\n提示:")
        print("- 首次运行会在exe同目录下创建 config.json 配置文件")
        print("- 可以通过系统托盘图标访问设置菜单")
        print("- 可以直接分发 dist\\工作时间进度.exe 文件")
    else:
        print("✗ 打包失败")
        print("=" * 50)
        print("\n请检查上方的错误信息")

    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
