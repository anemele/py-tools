#!/usr/bin/env python3.12

"""Auto execute command util success.

while <cond>:
    subprocess.run(<cmd>)"""

import argparse
import subprocess
from datetime import datetime
from typing import Sequence

DEFAULT_RETURN_CODE = 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cmd", type=str, nargs="+", help="command to execute")
    parser.add_argument("-e", type=int, help="expected return code")
    parser.add_argument("-u", type=int, nargs="*", help="unexpected return codes")

    args = parser.parse_args()
    # print(args)
    # return

    cmd: Sequence[str] = args.cmd
    expected: int | None = args.e
    unexpected: Sequence[int] | None = args.u

    begin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    if expected is not None:
        while subprocess.run(cmd).returncode != expected:
            count += 1
            print(f"... [{count}]\n")
    elif unexpected is not None:
        while subprocess.run(cmd).returncode in unexpected:
            count += 1
            print(f"... [{count}]\n")
    else:
        while subprocess.run(cmd).returncode != DEFAULT_RETURN_CODE:
            count += 1
            print(f"... [{count}]\n")
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("-" * 20)
    print(f"[INFO] from {begin} to {end}")
