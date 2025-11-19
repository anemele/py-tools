"""Common utilities."""

import glob
from itertools import chain
from os.path import isdir, isfile
from typing import Iterable


def human_readable_size(size_of_bytes: int) -> str:
    carry = 1024
    if size_of_bytes < carry:
        return f"{size_of_bytes} B"
    size = size_of_bytes
    for u in "KMGTPEZYBND":
        size /= carry
        if size < carry:
            return f"{size:.2f} {u}B"
    return f"{size:.2f} CB"


def glob_paths(
    patterns: Iterable[str],
    recursive: bool = False,
    *,
    only_file: bool = False,
    only_dir: bool = False,
) -> Iterable[str]:
    paths = chain.from_iterable(
        glob.iglob(pattern, recursive=recursive) for pattern in patterns
    )
    if only_file:
        paths = filter(isfile, paths)
    elif only_dir:
        paths = filter(isdir, paths)

    return paths
