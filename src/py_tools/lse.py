#!/usr/bin/env python3.12

"""List file extensions in a directory."""

import math
import os
import sys
import time
from collections import Counter

DIR_KEY = "DIR"
NUL_KEY = "NULL"


def get_ext(name: str) -> str:
    """what do special filenames return?
    .git    '.git' or ''
    README  'README' or ''
    """

    # if name.startswith('.') or '.' not in name:
    #     return name
    # return os.path.splitext(name)[1]

    # To distinguish default KEY, here use lower case.
    _, suffix = os.path.splitext(name)
    return suffix.lower() or NUL_KEY


def count_root(root: tuple[str, list[str], list[str]]) -> tuple[Counter[str], int]:
    _, d, f = root
    ld = len(d)
    counter = Counter({DIR_KEY: ld})
    counter.update(Counter(map(get_ext, f)))
    return counter, ld + len(f)


def list_types(directory: str, recursive: bool) -> tuple[Counter[str], int]:
    walker = os.walk(directory)
    counter, count = count_root(next(walker))

    if recursive:
        try:
            for ctr, c in map(count_root, walker):
                sys.stdout.write(f"\rcounting {count}")
                counter += ctr
                count += c
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write("\r")

    return counter, count


def pprint(counter: Counter, count: int):
    count_DIR = counter.pop(DIR_KEY)
    count_FILE = count - count_DIR

    ret = sorted(counter.items(), key=lambda x: x[1])
    if len(ret) == 0:
        SPAN_WIDTH = 0
    else:
        SPAN_WIDTH = math.ceil(math.log10(ret[-1][1] + 1))
    print("-" * (SPAN_WIDTH + 18))  # + length of `counting `
    for e, c in ret:
        print(f"    {c:>{SPAN_WIDTH}d}  {e}")

    print(f"\n  {count_FILE} file(s)  {count_DIR} dir(s)    {count:,} total")


def run(directory: str, recursive: bool):
    if not os.path.isdir(directory):
        print(f"not a dir: {directory}")
        return

    print(directory)
    begin = time.perf_counter()
    counter, count = list_types(directory, recursive)
    pprint(counter, count)
    print(f" cost time: {time.perf_counter() - begin:.3f}s")


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dir",
        type=str,
        nargs="?",
        default=".",
        help="default: current directory",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="recursive",
    )
    args = parser.parse_args()
    # print(args)
    # return

    args_dir: str = args.dir
    args_r: bool = args.recursive

    run(args_dir, args_r)
