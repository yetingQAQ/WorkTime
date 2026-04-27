#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build helper for PyInstaller.

Usage examples:
  python build.py
  python build.py --mode aggressive
  python build.py --mode safe --distpath dist_safe --workpath build_safe
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


MODE_SAFE = "safe"
MODE_AGGRESSIVE = "aggressive"


def run(cmd: list[str], description: str, env: dict[str, str] | None = None) -> None:
    print(f"\n{description}...")
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"{description} failed (exit code {result.returncode})")


def format_size(size: int) -> str:
    mb = size / (1024 * 1024)
    return f"{size} bytes ({mb:.2f} MB)"


def clean_dir(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        shutil.rmtree(path)
        return True
    except OSError:
        return False


def find_built_exe(distpath: Path) -> Path | None:
    exes = sorted(distpath.glob("*.exe"))
    if exes:
        return exes[0]
    return None


def default_paths(mode: str) -> tuple[Path, Path]:
    if mode == MODE_SAFE:
        return Path("build"), Path("dist")
    return Path("build_aggressive"), Path("dist_aggressive")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build executable with PyInstaller")
    parser.add_argument(
        "--mode",
        choices=[MODE_SAFE, MODE_AGGRESSIVE],
        default=MODE_SAFE,
        help="safe: keep software OpenGL fallback; aggressive: smaller package.",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="skip `uv sync --extra build`",
    )
    parser.add_argument(
        "--distpath",
        default=None,
        help="PyInstaller dist output path",
    )
    parser.add_argument(
        "--workpath",
        default=None,
        help="PyInstaller build/work path",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="only clean output folders, do not build",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    default_workpath, default_distpath = default_paths(args.mode)
    workpath = Path(args.workpath) if args.workpath else default_workpath
    distpath = Path(args.distpath) if args.distpath else default_distpath

    print("=" * 58)
    print("WorkTime Build Script")
    print("=" * 58)
    print(f"Mode      : {args.mode}")
    print(f"Work path : {workpath}")
    print(f"Dist path : {distpath}")

    # 1) Check uv availability
    print("\n[1/5] Checking uv...")
    uv_check = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    if uv_check.returncode != 0:
        print("Error: `uv` not found. Install with: pip install uv")
        return 1
    print(f"uv version: {uv_check.stdout.strip()}")

    # 2) Sync dependencies
    print("\n[2/5] Syncing dependencies...")
    if args.no_sync:
        print("Skipped (use --no-sync)")
    else:
        run(["uv", "sync", "--extra", "build"], "Sync dependencies")

    # 3) Prepare build environment variables
    print("\n[3/5] Preparing build environment...")
    build_env = os.environ.copy()
    if args.mode == MODE_AGGRESSIVE:
        build_env["DROP_SOFTWARE_OPENGL"] = "1"
        print("Enabled: DROP_SOFTWARE_OPENGL=1")
    else:
        build_env.pop("DROP_SOFTWARE_OPENGL", None)
        print("Enabled: compatibility mode (software OpenGL fallback kept)")

    # 4) Clean old outputs
    print("\n[4/5] Cleaning previous outputs...")
    work_clean = clean_dir(workpath)
    dist_clean = clean_dir(distpath)
    if not work_clean:
        print(f"Warning: cannot remove {workpath}; it may be in use.")
    if not dist_clean:
        print(f"Warning: cannot remove {distpath}; it may be in use.")
    if args.clean_only:
        print("\nClean completed.")
        return 0

    # 5) Build with PyInstaller
    print("\n[5/5] Building executable...")
    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--workpath",
        str(workpath),
        "--distpath",
        str(distpath),
        "build.spec",
    ]
    run(cmd, "Build executable", env=build_env)

    exe = find_built_exe(distpath)
    print("\n" + "=" * 58)
    if exe and exe.exists():
        print("Build succeeded")
        print(f"Output : {exe.resolve()}")
        print(f"Size   : {format_size(exe.stat().st_size)}")
    else:
        print("Build finished but executable was not found in dist path.")
        return 1

    print("=" * 58)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"\nError: {exc}")
        raise SystemExit(1)
