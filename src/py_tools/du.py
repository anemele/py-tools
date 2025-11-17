#!/usr/bin/env python3

"""Disk usage? I don't know."""

import argparse
import os
import os.path as osp
import time
from typing import Iterable, Set

type T_OS_WALKER = tuple[str, list[str], list[str]]
type T_ITEM = tuple[int, int, int]


def count_root(root: T_OS_WALKER) -> T_ITEM:
    """return a tuple of
    (number of dirs, number of files, size of files)"""
    r, d, f = root
    pth = (osp.join(r, i) for i in f)
    return len(d), len(f), sum(map(osp.getsize, pth))


def count(directory: str, recursive: bool) -> Iterable[T_ITEM]:
    inode_set = set()
    tmp = os.walk(directory)

    first = trim_hardlinks_from_root(inode_set, next(tmp))
    yield count_root(first)

    if recursive:
        tmp = (trim_hardlinks_from_root(inode_set, i) for i in tmp)
        yield from map(count_root, tmp)


def trim_hardlinks_from_root(inode_set: Set[int], root: T_OS_WALKER) -> T_OS_WALKER:
    r, d, f = root
    new_f = []
    for i in f:
        ff = osp.join(r, i)
        inode = os.stat(ff).st_ino
        if inode in inode_set:
            continue
        new_f.append(i)
        inode_set.add(inode)
    return r, d, new_f


def human_readable_size(size: float) -> str:
    units = tuple(f"{x}B" for x in ",K,M,G,T,P,E,Z,Y,B,N,D,C".split(","))
    max_idx = len(units) - 1
    carry = 1024
    idx = 0
    while idx < max_idx and size >= carry:
        idx += 1
        size /= carry

    return f"{size:.2f} {units[idx]}"


def run(director: str, recursive: bool = True):
    print("\n", osp.abspath(director), "\n")
    begin = time.perf_counter()
    nd, nf, ns = 0, 0, 0
    try:
        for d, f, s in count(director, recursive):
            nd += d
            nf += f
            ns += s
            print(f"\r  {nd} dir(s)  {nf} file(s)  {ns:,} bytes", end="", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        end = time.perf_counter()
        h = human_readable_size(ns)
        print(f" ({h})")
        print(f"\n cost time: {end - begin:.3f}s")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dir",
        type=str,
        nargs="?",
        default=".",
        help="default: current directory",
    )
    parser.add_argument(
        "-R",
        "--no-recursive",
        action="store_true",
        help="don't recurse into subdirectories",
    )

    args = parser.parse_args()
    # print(args)
    # return
    arg_dir: str = args.dir
    arg_R: bool = args.no_recursive

    if not osp.isdir(arg_dir):
        print(f"not a dir: {arg_dir}")
    else:
        run(arg_dir, not arg_R)
