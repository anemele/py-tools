#!/usr/bin/env python3.12
"""rename file or directory with some pattern"""

import argparse
import hashlib
import random
import string
from functools import wraps
from pathlib import Path
from typing import Callable, Literal, Optional, Sequence

from ._common import glob_paths


def _inform(old: str | Path, new: str | Path, msg: str = "done"):
    print(f"{msg}: {old} --> {new}")


def rename_random(path: Path):
    def rng():
        chars = string.ascii_lowercase + string.digits
        char_list = random.choices(chars, k=6)
        return "".join(char_list)

    while True:
        new_path = path.with_stem(rng())  # 3.9+
        if not new_path.exists():
            break

    path.rename(new_path)
    _inform(path, new_path)


Algo = Literal["md5", "sha1", "sha256"]


def rename_hashsum(path: Path, alg: Algo):
    try:
        content = path.read_bytes()
    except IOError as e:
        print(e)
        return

    hashsum = hashlib.new(alg, content)
    new_path = path.with_stem(hashsum.hexdigest())

    if new_path == path or new_path.exists():
        _inform(path, new_path, "exists")
    else:
        path.rename(new_path)
        _inform(path, new_path)


def rename_lower(path: Path):
    new_path = path.rename(path.with_name(path.name.lower()))
    _inform(path, new_path)


def rename_upper(path: Path):
    new_path = path.rename(path.with_name(path.name.upper()))
    _inform(path, new_path)


def if_exist_then_rename(func: Callable[[Path, str], Path | None]):
    @wraps(func)
    def wrapper(path: Path, xfix: str):
        try:
            new_path = func(path, xfix)
        except ValueError as e:
            print(e)
            return

        if new_path is None:
            # print(f'{func.__name__} returns None')
            return

        if new_path.exists():
            _inform(path, new_path, "exists")
        else:
            path.rename(new_path)
            _inform(path, new_path)

    return wrapper


@if_exist_then_rename
def rename_remove_prefix(path: Path, prefix: str) -> Path | None:
    name = path.name

    if not name.startswith(prefix):
        # print(f'not start with `{prefix}`: {path}')
        return

    return path.with_name(name.lstrip(prefix))


@if_exist_then_rename
def rename_add_prefix(path: Path, prefix: str) -> Path:
    """prepend prefix"""
    return path.with_name(f"{prefix}{path.name}")


@if_exist_then_rename
def rename_remove_suffix(path: Path, suffix: str) -> Path | None:
    name = path.stem

    if not name.endswith(suffix):
        # print(f'not end with `{suffix}`: {path}')
        return

    return path.with_name(name.rstrip(suffix))


@if_exist_then_rename
def rename_add_suffix(path: Path, suffix: str) -> Path:
    return path.with_stem(f"{path.stem}{suffix}")


def main():
    parser = argparse.ArgumentParser(
        prog=None,
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", nargs="+", help="file or directory, glob is supported")

    # filter
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument("-f", "--only-file", action="store_true", default=False)
    filters.add_argument("-d", "--only-dir", action="store_true", default=False)

    # supported patterns
    patterns = parser.add_mutually_exclusive_group()
    # patterns.add_argument("--random", action="store_true", default=False)
    patterns.add_argument("--hashsum", help="hashsum algorithm")
    patterns.add_argument("--lower", action="store_true", default=False)
    patterns.add_argument("--upper", action="store_true", default=False)
    patterns.add_argument("--add-prefix")
    patterns.add_argument("--add-suffix")
    patterns.add_argument("--remove-prefix")
    patterns.add_argument("--remove-suffix")

    # parse args
    args = parser.parse_args()

    arg_path: Sequence[str] = args.path
    arg_only_file: bool = args.only_file
    arg_only_dir: bool = args.only_dir

    # arg_ptn_random: bool = args.random
    arg_ptn_hashsum: Optional[Algo] = args.hashsum
    arg_ptn_lower: bool = args.lower
    arg_ptn_upper: bool = args.upper
    arg_ptn_add_prefix: Optional[str] = args.add_prefix
    arg_ptn_add_suffix: Optional[str] = args.add_suffix
    arg_ptn_remove_prefix: Optional[str] = args.remove_prefix
    arg_ptn_remove_suffix: Optional[str] = args.remove_suffix

    # get path list
    paths = glob_paths(arg_path, only_file=arg_only_file, only_dir=arg_only_dir)
    paths = map(Path, paths)

    # match pattern
    # if arg_ptn_random:
    #     for f in fs:
    #         rename_random(f)
    # elif arg_ptn_lower:
    if arg_ptn_lower:
        for path in paths:
            rename_lower(path)
    elif arg_ptn_upper:
        for path in paths:
            rename_upper(path)
    elif arg_ptn_hashsum is not None:
        for path in paths:
            rename_hashsum(path, arg_ptn_hashsum)
    elif arg_ptn_add_prefix is not None:
        for path in paths:
            rename_add_prefix(path, arg_ptn_add_prefix)
    elif arg_ptn_add_suffix is not None:
        for path in paths:
            rename_add_suffix(path, arg_ptn_add_suffix)
    elif arg_ptn_remove_prefix is not None:
        for path in paths:
            rename_remove_prefix(path, arg_ptn_remove_prefix)
    elif arg_ptn_remove_suffix is not None:
        for path in paths:
            rename_remove_suffix(path, arg_ptn_remove_suffix)
    else:
        for path in paths:
            rename_random(path)
