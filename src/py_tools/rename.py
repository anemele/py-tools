#!/usr/bin/env python3.12
"""rename file or directory with some pattern"""

import argparse
import hashlib
import random
import re
import string
from enum import StrEnum
from pathlib import Path
from typing import Callable, Sequence

from ._common import glob_paths

type RenameFunc = Callable[[Path], Path]


def rename_random(path: Path) -> Path:
    chars = string.ascii_lowercase + string.digits

    def rng():
        char_list = random.choices(chars, k=random.randint(4, 8))
        return "".join(char_list)

    while True:
        new_path = path.with_stem(rng())  # 3.9+
        if not new_path.exists():
            return new_path


def rename_substitute(s: tuple[str, str]) -> RenameFunc:
    p, r = s

    try:
        sub = re.compile(p).sub
    except re.error as e:
        raise ValueError(f"invalid regex {p}") from e

    def f(path: Path):
        return path.with_stem(sub(r, path.stem))

    return f


class ToWhat(StrEnum):
    # generate a random name consisting of [a-z0-9]
    RANDOM = "random"
    # case related
    LOWER = "lower"
    UPPER = "upper"
    SWAPCASE = "swap"
    CAPITALIZE = "caps"
    TITLE = "title"
    # hashsum related
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    # remove extension name
    NO_EXT = "no-ext"


def rename_convert(s: str) -> RenameFunc:
    t = ToWhat
    match s:
        case t.RANDOM:
            return rename_random

        case t.LOWER | t.UPPER | t.SWAPCASE | t.CAPITALIZE | t.TITLE:
            case_method = {
                t.LOWER: str.lower,
                t.UPPER: str.upper,
                t.SWAPCASE: str.swapcase,
                t.CAPITALIZE: str.capitalize,
                t.TITLE: str.capitalize,
            }[s]

            def f(path: Path) -> Path:
                return path.with_name(case_method(path.name))

        case t.MD5 | t.SHA1 | t.SHA256:

            def f(path: Path) -> Path:
                with path.open("rb") as fp:
                    hashsum = hashlib.file_digest(fp, s)

                return path.with_stem(hashsum.hexdigest())

        case t.NO_EXT:

            def f(path: Path) -> Path:
                return path.with_suffix("")

        case _:
            # should never reach here
            raise ValueError(f"unknown to-what: {s}")

    return f


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", nargs="+", help="file or directory, glob is supported")
    parser.add_argument("--dry-run", action="store_true", default=False)

    # method
    methods = parser.add_mutually_exclusive_group(required=True)
    methods.add_argument("-t", "--to", help=" | ".join(m.value for m in ToWhat))
    methods.add_argument("-s", "--sub", nargs=2, help="<regex> <repl>")

    # filter
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument("-f", "--only-file", action="store_true", default=False)
    filters.add_argument("-d", "--only-dir", action="store_true", default=False)

    # parse args
    args = parser.parse_args()

    arg_path: Sequence[str] = args.path
    dry_run: bool = args.dry_run
    to: str | None = args.to
    sub: tuple[str, str] | None = args.sub
    only_file: bool = args.only_file
    only_dir: bool = args.only_dir

    try:
        if to is not None:
            rename_func = rename_convert(to)
        elif sub is not None:
            rename_func = rename_substitute(sub)
        else:
            assert False, "should never reach here"

    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # get path list
    paths = glob_paths(arg_path, only_file=only_file, only_dir=only_dir)
    paths = map(Path, paths)

    for path in paths:
        try:
            new_path = rename_func(path)
        except Exception as e:
            print(f"[ERROR] {e}")
            continue

        if dry_run:
            print(f"[DRY-RUN] {path} -> {new_path}")
            continue

        try:
            # rename even if be the same
            path.rename(new_path)
        except OSError as e:
            print(f"[ERROR] {e}")
        else:
            print(f"[DONE] {path} -> {new_path}")
