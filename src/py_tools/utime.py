#!/usr/bin/env python3

"""设置文件/目录的访问时间和修改时间

os.utime(path, time: (atime, mtime)=None, *, ...)

时间包括年、月、日、时、分、秒，可以简写。
例如 2020-02-20 20:02:20 简写为 20 2 20 20 2 20
"""

import os
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence

from ._common import glob_paths


def get_timestamp(ftime: str | None) -> float | None:
    if ftime is None:
        return time.time()
    try:
        ptime = time.strptime(ftime, "%y %m %d %H %M %S")
        return time.mktime(ptime)
    except ValueError:
        return


def set_utime(paths: Iterable[Path], timestamp: float) -> tuple[int, int]:
    count = 0
    succ = 0
    for succ, path in enumerate(paths, 1):
        sys.stdout.write(f"\rSetting {path}")
        try:
            os.utime(path, (timestamp, timestamp))
            count += 1
        except Exception as e:
            print(f"\r{e}")
    return succ, count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file", nargs="+", help="file/folder path")
    parser.add_argument("--ftime", help="format time, now by default.")
    parser.add_argument("-r", "--recursive", action="store_true")

    mut_grp = parser.add_mutually_exclusive_group()
    mut_grp.add_argument("--only-file", action="store_true")
    mut_grp.add_argument("--only-dir", action="store_true")

    args = parser.parse_args()
    # print(args)
    # return

    items: Sequence[str] = args.file
    ftime: str | None = args.ftime
    is_recursive: bool = args.recursive
    only_file: bool = args.only_file
    only_dir: bool = args.only_dir

    timestamp = get_timestamp(ftime)
    if timestamp is None:
        print("Invalid time format.")
        return

    paths = glob_paths(items, is_recursive, only_file=only_file, only_dir=only_dir)
    paths = map(Path, paths)

    s, c = set_utime(paths, timestamp)
    print(f"\rDone: {s}/{c}")
