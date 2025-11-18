#!/usr/bin/env python3.12

# There is a bug using Python 3.12.0, 3.12.1
# It returns negative value of a/c/mtime of "System Volume Information"
# See https://github.com/python/cpython/issues/111877

# This bug is fixed in 3.12.2

import glob
import os
import time
from itertools import chain


def stat_file(path: str) -> str:
    stat = os.stat(path)
    info = (
        ("-" * 40, ""),
        ("path", path),
        ("inode", stat.st_ino),
        ("dev", stat.st_dev),
        ("nlink", stat.st_nlink),
        ("size", readable_size(stat.st_size)),
        ("ctime", readable_date(stat.st_birthtime)),
        ("mtime", readable_date(stat.st_mtime)),
        ("atime", readable_date(stat.st_atime)),
    )
    return "\n".join(f"{k:6}{v}" for k, v in info)


def readable_size(size: float) -> str:
    if size < 1024:
        return f"{size:0f} B"
    for u in "KMGTP":
        if size < 1024:
            return f"{size:.2f} {u}B"
        size /= 1024
    return f"{size:.2f} EB"


def readable_date(second: float):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(second))


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=str, nargs="+", help="")
    args = parser.parse_args()
    # print(args)
    # return
    files = chain.from_iterable(map(glob.iglob, args.file))
    for file in files:
        print(stat_file(file))
