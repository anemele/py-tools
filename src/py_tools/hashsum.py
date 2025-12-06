"""Calculate file hashsum.

Given file path, or read from stdin.
Glob supported."""

import argparse
import hashlib
import os.path as op
import sys
from dataclasses import dataclass

from ._common import glob_paths


@dataclass
class HashLine:
    digest: str
    path: str

    def __str__(self) -> str:
        return f"{self.digest}  {self.path}"


def hash_file(alg: str, file: str) -> HashLine:
    with open(file, "rb") as fp:
        # 3.11+
        obj = hashlib.file_digest(fp, alg)
    return HashLine(obj.hexdigest(), str(file))


def check_sum(alg: str, file: str) -> None:
    with open(file) as fp:
        for line in fp:
            tmp = line.strip().split()
            if len(tmp) != 2:
                # print(f'bad line: {line}')
                continue
            digest, file = tmp
            if not op.exists(file):
                # print(f'not found: {file}')
                continue
            hash_line = hash_file(alg, file)
            if hash_line.digest == digest:
                print(f"OK: {file}")
            else:
                print(f"do NOT match: {file}")


def gen_main(alg):
    def main():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("file", nargs="*", help="files to hash")
        parser.add_argument(
            "--check", "-c", action="store_true", help="check a hash sum file"
        )

        args = parser.parse_args()
        files = args.file
        is_check: bool = args.check

        if len(files) == 0 and not sys.stdin.isatty():
            files = sys.stdin.read().splitlines()
        if len(files) == 0:
            parser.print_help()
            parser.exit(1)

        files = glob_paths(files, only_file=True)

        if is_check:
            for file in files:
                check_sum(alg, file)
            return

        for file in files:
            line = hash_file(alg, file)
            print(line)

    return main


md5 = gen_main("md5")
sha1 = gen_main("sha1")
sha224 = gen_main("sha224")
sha256 = gen_main("sha256")
sha384 = gen_main("sha384")
sha512 = gen_main("sha512")
