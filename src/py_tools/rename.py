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


def rename_substitute(subexpr: str) -> RenameFunc:
    if not subexpr.startswith("s/") or not subexpr.endswith("/"):
        raise ValueError(f"substitute expr {subexpr} not match s/str/repl/")

    s = subexpr.removeprefix("s/").removesuffix("/").split("/")
    if len(s) != 2:
        raise ValueError(f"substitute expr {subexpr} not match s/str/repl/")
    p, r = s

    try:
        sub = re.compile(p).sub
    except re.error as e:
        raise ValueError(f"invalid reg expr {subexpr}") from e

    def f(path: Path):
        return path.with_stem(sub(r, path.stem))

    return f


class ToWhat(StrEnum):
    RANDOM = "random"
    LOWER = "lower"
    UPPER = "upper"
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    NO_EXT = "no-ext"


def dispatch(arg: ToWhat | str) -> RenameFunc:
    try:
        arg = ToWhat(arg)
    except ValueError:
        return rename_substitute(arg)

    t = ToWhat
    match arg:
        case t.RANDOM:
            return rename_random
        case t.LOWER:

            def f(path: Path) -> Path:
                return path.with_name(path.name.lower())

        case t.UPPER:

            def f(path: Path) -> Path:
                return path.with_name(path.name.upper())

        case t.MD5 | t.SHA1 | t.SHA256:

            def f(path: Path) -> Path:
                with path.open("rb") as fp:
                    hashsum = hashlib.file_digest(fp, arg)

                return path.with_stem(hashsum.hexdigest())

        case t.NO_EXT:

            def f(path: Path) -> Path:
                return path.with_suffix("")

        case _:
            # should never reach here
            raise ValueError(f"unknown to-what {arg}")

    return f


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", nargs="+", help="file or directory, glob is supported")
    parser.add_argument(
        "--to",
        required=True,
        help=" | ".join(m.value for m in ToWhat) + " | s/str/repl/",
    )
    parser.add_argument("--dry-run", action="store_true", default=False)

    # filter
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument("-f", "--only-file", action="store_true", default=False)
    filters.add_argument("-d", "--only-dir", action="store_true", default=False)

    # parse args
    args = parser.parse_args()

    arg_path: Sequence[str] = args.path
    arg_to: ToWhat | str = args.to
    dry_run: bool = args.dry_run
    only_file: bool = args.only_file
    only_dir: bool = args.only_dir

    try:
        rename_func = dispatch(arg_to)
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

        if new_path == path:
            print(f"[SKIP] exists {new_path}")
            continue

        try:
            path.rename(new_path)
        except OSError as e:
            print(f"[ERROR] {e}")
        else:
            print(f"[DONE] {path} -> {new_path}")
