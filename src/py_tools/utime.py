#!/usr/bin/env python3

"""Set the access and modified times,
os.utime(path, time: (atime, mtime)=None, *, ...)"""

import argparse
import os
import sys
import time
from itertools import chain
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

TYPE_ITEMS = Iterable[Path]
TIME_FORMAT = "%y %m %d %H %M %S"


def get_timestamp(ftime: Optional[str]) -> float:
    if ftime is None:
        return time.time()
    try:
        ptime = time.strptime(ftime, TIME_FORMAT)
        return time.mktime(ptime)
    except ValueError as e:
        print(e)
        print("[Warning] Format error, use now time instead.")
        return time.time()


def set_utime(
    item_list: TYPE_ITEMS,
    timestamp: float,
) -> Tuple[int, int]:
    count = 0
    i = -1
    for i, item in enumerate(item_list):
        sys.stdout.write(f"\rSetting {i + 1}")
        try:
            os.utime(item, (timestamp, timestamp))
        except Exception as e:
            print(f"\r{e}")
            continue
        count += 1
    return count, i + 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "item",
        type=Path,
        nargs="+",
        help="files or folders",
    )
    parser.add_argument(
        "--ftime",
        type=str,
        help="format time, now by default. `2020-02-20 20:02:20` --> `20 2 20 20 2 20`",
    )
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("--only-file", action="store_true")
    parser.add_argument("--only-dir", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    # print(args)
    # return

    args_item: List[Path] = args.item
    args_ftime: Optional[str] = args.ftime
    args_recursive: bool = args.recursive
    args_only_file: bool = args.only_file
    args_only_dir: bool = args.only_dir

    items: TYPE_ITEMS
    if args_recursive:
        items = chain(args_item, *(p.rglob("*") for p in args_item))
    else:
        items = args_item

    if args_only_file and args_only_dir:
        print("[INFO] nothing to do.")
        return

    if args_only_file:
        items = filter(lambda p: p.is_file(), items)
    if args_only_dir:
        items = filter(lambda p: p.is_dir(), items)

    timestamp = get_timestamp(args_ftime)
    c, i = set_utime(items, timestamp=timestamp)
    print(f"\rAll items: {i}, set items: {c}")
