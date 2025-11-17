#!/usr/bin/env python3
r"""
Fix python env on Windows.

Python 虚拟环境移动位置后，因为 bin 目录下面的程序嵌入了绝对路径导致无法使用。
一种简单直接的办法是删除该虚拟环境，重新安装。
这种方法消耗太大，更好的方法是修改这些绝对路径。

Windows 绝对路径以盘符开头，路径中间可能有 Scripts 目录。
例如 C:\path\to\env\Scripts\python.exe

本程序接受一个路径参数 root 指向移动后的虚拟环境。
读取 root\Scripts 目录下的所有文件（除了 python.exe 和 pythonw.exe），
匹配其中绝对路径，与 root 进行比较，如果不同，则修改为 root。

exe 文件匹配项以 Scripts\python.exe 结尾，通常准确。
activate* 文件只包含 root 部分，可能出现差错，设置盘符只匹配 C-Z 大写可以减少误判。
"""

import re
from pathlib import Path

BIN_DIR = "Scripts"

# 这里的 [\w\.\\-] 是匹配中间路径的，可能不全导致出错，记得修改
PATTERN_EXE = re.compile(r"#!([C-Zc-z]:\\[\w\.\\-]+?)\\Scripts\\python\.exe".encode())
PATTERN_ACTIVATE = re.compile(r"([C-Z]:\\[\w\.\\-]+)".encode())


def check_venv(root: Path) -> bool:
    return root.joinpath("pyvenv.cfg").exists() and root.joinpath(BIN_DIR).exists()


def fix_file(path: Path, pattern: re.Pattern[bytes]) -> bool:
    r = path.read_bytes()
    s = pattern.search(r)
    if s is None:
        # 此处应有提示
        return False

    p: bytes = s.group(1)
    t = bytes(path.parent.parent.absolute())
    if p == t:
        return False

    try:
        path.write_bytes(r.replace(p, t))
        print(f"Done: {path}")
        return True
    except PermissionError:
        print(f"Error: cannot modify {path}")
        return False


def fix_env(root: Path):
    count = 0

    exes = root.joinpath(BIN_DIR).glob("*.exe")
    for exe in exes:
        if exe.name == "python.exe" or exe.name == "pythonw.exe":
            continue
        if fix_file(exe, PATTERN_EXE):
            count += 1

    activates = root.joinpath(BIN_DIR).glob("activate*")
    for activate in activates:
        if fix_file(activate, PATTERN_ACTIVATE):
            count += 1

    if count == 0:
        print("This env is OK")
        return


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("root", type=Path, help="venv root path")
    args = parser.parse_args()

    root: Path = args.root

    fix_env(root)
