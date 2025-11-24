#!/usr/bin/env python3.12
"""rename file or directory with some pattern"""

import argparse
import hashlib
import random
import re
import string
from functools import partial
from pathlib import Path
from typing import Callable, Literal, Optional, Sequence

from ._common import glob_paths

type RenameFunc = Callable[[Path], Path]
ToWhat = Literal[
    "random",
    "lower",
    "upper",
    "md5",
    "sha1",
    "sha256",
    "no-ext",
]


def rename_random(path: Path) -> Path:
    chars = string.ascii_lowercase + string.digits

    def rng():
        char_list = random.choices(chars, k=random.randint(4, 8))
        return "".join(char_list)

    while True:
        new_path = path.with_stem(rng())  # 3.9+
        if not new_path.exists():
            return new_path


def rename_lower(path: Path) -> Path:
    return path.with_name(path.name.lower())


def rename_upper(path: Path) -> Path:
    return path.with_name(path.name.upper())


def rename_hashsum(path: Path, alg: str) -> Path:
    with path.open("rb") as fp:
        hashsum = hashlib.file_digest(fp, alg)

    return path.with_stem(hashsum.hexdigest())


def rename_remove_ext(path: Path) -> Path:
    return path.with_suffix("")


def wrap(arg: ToWhat | str) -> RenameFunc:
    match arg:
        case "random":
            return rename_random
        case "lower":
            return rename_lower
        case "upper":
            return rename_upper
        case "md5" | "sha1" | "sha256":
            return partial(rename_hashsum, alg=arg)
        case "no-ext":
            return rename_remove_ext
        case _:
            # substitute
            if not arg.startswith("s/") or not arg.endswith("/"):
                raise ValueError(f"substitute expr {arg} not match s/str/repl/")

            s = arg.removeprefix("s/").removesuffix("/").split("/")
            if len(s) != 2:
                raise ValueError(f"substitute expr {arg} not match s/str/repl/")
            p, r = s

            try:
                sub = re.compile(p).sub
            except re.error as e:
                raise ValueError(f"invalid reg expr {arg}") from e

            def f(path: Path):
                return path.with_stem(sub(r, path.stem))

            return f


def main():
    parser = argparse.ArgumentParser(
        prog=None,
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", nargs="+", help="file or directory, glob is supported")
    parser.add_argument("--to", help="|".join(ToWhat.__args__) + "| s/str/repl/")
    parser.add_argument("--dry-run", action="store_true", default=False)

    # filter
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument("-f", "--only-file", action="store_true", default=False)
    filters.add_argument("-d", "--only-dir", action="store_true", default=False)

    # parse args
    args = parser.parse_args()

    arg_path: Sequence[str] = args.path
    arg_to: Optional[ToWhat | str] = args.to
    dry_run: bool = args.dry_run
    only_file: bool = args.only_file
    only_dir: bool = args.only_dir

    try:
        rename_func = wrap(arg_to or "random")
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # get path list
    paths = glob_paths(arg_path, only_file=only_file, only_dir=only_dir)
    paths = map(Path, paths)

    for path in paths:
        new_path = rename_func(path)
        if new_path.exists():
            print(f"[SKIP] exists {new_path}")
        else:
            if dry_run:
                print(f"[DRY-RUN] {path} -> {new_path}")
                continue
            try:
                path.rename(new_path)
            except OSError as e:
                print(f"[ERROR] {e}")
            else:
                print(f"[DONE] {path} -> {new_path}")
