#!/usr/bin/env python3.12

# There is a bug using Python 3.12.0, 3.12.1
# It returns negative value of a/c/mtime of "System Volume Information"
# See https://github.com/python/cpython/issues/111877

# This bug is fixed in 3.12.2

import os
import time

from ._common import glob_paths, human_readable_size


def stat_file(path: str) -> str:
    info = os.stat(path)
    fmt_info = f"""\
  File: {path}
  Size: {info.st_size} ({human_readable_size(info.st_size)})
Device: {info.st_dev}  Inode: {info.st_ino}  Links: {info.st_nlink}
Access: {readable_date(info.st_atime)}
Modify: {readable_date(info.st_mtime)}
 Birth: {readable_date(info.st_birthtime)}
"""
    return fmt_info


def readable_date(second: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(second))


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=str, nargs="+", help="")
    args = parser.parse_args()

    for path in glob_paths(args.path):
        print(stat_file(path))
