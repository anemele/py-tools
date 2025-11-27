#!/usr/bin/env python3.12
"""Get Python releases version and date"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Self  # v3.11+
from urllib.request import urlopen

url = "https://www.python.org/downloads/"


@dataclass
class SemVer:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, ver: str) -> Self:
        tmp = ver.split(".")[:3]
        return cls(*map(int, tmp))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, sv: Self) -> bool:
        # fmt: off
        return (
            self.major < sv.major
            or self.major == sv.major and self.minor < sv.minor
            or self.major == sv.major and self.minor == sv.minor and self.patch < sv.patch
        )
        # fmt: on


trans_tab = {
    "April": 4,
    "Oct.": 10,
    "May": 5,
    "July": 7,
    "Sept.": 9,
    "Dec.": 12,
    "Nov.": 11,
    "Feb.": 2,
    "March": 3,
    "June": 6,
    "Jan.": 1,
    "Aug.": 8,
}


def parse_date(date: str) -> str:
    key, day, year = date.split()
    return f"{year}-{trans_tab[key]}-{day[:-1]}"


@dataclass
class VerDate:
    ver: SemVer
    date: datetime

    def __str__(self) -> str:
        return f"{self.ver}\t{self.date.date()}"


def get_ver_date() -> Iterable[VerDate]:
    with urlopen(url) as fs:
        data = fs.read()

    # v3.12 sets "Accept-Encoding:gzip, deflate"
    # Here needs decompress first.
    # html = gzip.decompress(data).decode()

    # NOTE: It seems no need to decompress now.
    html = data.decode()

    matches = re.findall(
        r'>Python (\d(?:\.\d+){2})[\s\S]+?"release-date">(\w+\.? \d{1,2}, \d{4})',
        html,
    )
    ver_data = (
        VerDate(SemVer.parse(ver), datetime.strptime(parse_date(date), "%Y-%m-%d"))
        for ver, date in matches
    )

    return ver_data


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bydate", action="store_true", help="Sort by date")
    parser.add_argument(
        "-r", "--reverse", action="store_true", help="Reverse the output order"
    )

    args = parser.parse_args()

    ver_data = get_ver_date()
    items = sorted(
        ver_data,
        key=(lambda x: x.date) if args.bydate else (lambda x: x.ver),
        reverse=args.reverse,
    )
    for item in items:
        print(item)
