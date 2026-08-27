import re
import string
from collections.abc import Sequence


class NumeralSystem:
    def __init__(
        self, char_set: Sequence[str] = string.digits + string.ascii_lowercase
    ) -> None:
        """default character set is
        0123456789abcdefghijklmnopqrstuvwxyz
        """

        length = len(char_set)
        if length < 2:
            raise ValueError("requires at least 2 char in char_set")
        if length > len(set(char_set)):
            raise ValueError("requires no-repeat char sequence.")

        self._char_vec = char_set
        self._char_map = {c: i for i, c in enumerate(char_set)}
        self._base = length

        re_seq = "".join(re.escape(c) for c in char_set)
        # not guarantee the suffix
        self._valid_regex = re.compile(rf"([{re_seq}]+)(_\d+)?")

    def __repr__(self):
        return f"{self.__class__} base={self._base} char={self._char_vec}"

    def _int_to_any(self, number: int, base: int) -> str:
        tmp = []
        while number != 0:
            number, i = divmod(number, base)
            tmp.append(self._char_vec[i])
        return "".join(tmp[::-1])

    def _any_to_int(self, number: str, base: int) -> int:
        return sum(base**p * self._char_map[c] for p, c in enumerate(number[::-1]))

    def _parse(self, number: str, to_base: int) -> tuple[str, int]:
        s = self._valid_regex.match(number)
        if s is None:
            raise ValueError(f"{number} is not a valid number")

        number = s.group(1)
        if (b := s.group(2)) is None:
            base = 10
        else:
            base = int(b[1:])

        _base = self._base
        if not 2 <= to_base <= _base:
            raise ValueError(f"{to_base} out of range [2, {_base}]")
        if not 2 <= base <= _base:
            raise ValueError(f"{base} out of range [2, {_base}]")

        if not set(number).issubset(set(self._char_vec[:base])):
            raise ValueError(f"{number} contains invalid char")

        return number, base

    def convert(self, number: str, to_base: int = 10) -> str:
        r"""
        number: a str [{char_set}]+(:?_\d+)?, default 10
        to_base: a int in range [2, {_base}], default 10

        e.g.
        convert('1110_2') # 14_10
        convert('1011_2', 8) # 13_8
        """
        number, base = self._parse(number, to_base)

        if to_base == base:
            to_number = number
        else:
            tmp = self._any_to_int(number, base)
            to_number = self._int_to_any(tmp, to_base)

        return f"{to_number}_{to_base}"


def main():
    import argparse
    from textwrap import dedent

    cvtnum = NumeralSystem().convert
    doc = cvtnum.__doc__.format(char_set="0-9a-z", _base=36)  # type: ignore
    parser = argparse.ArgumentParser(
        description=dedent(doc),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("number", type=str, nargs="?", help="number to convert")
    parser.add_argument(
        "to_base", type=int, nargs="?", default=10, help="base to convert"
    )

    args = parser.parse_args()

    number: str | None = args.number
    to_base: int = args.to_base

    if number is not None:
        try:
            nn = cvtnum(number, to_base)
            print(nn)
        except ValueError as e:
            print(f"Error: {e}")
        return

    # repl
    print("## NUMSYS REPL ##")
    print(" INPUT: <number> [to_base]\n  or empty line to exit")
    while True:
        line = input(f"\n{to_base} : ").strip()
        if not line:
            print("END")
            break
        tmp = line.split()
        match len(tmp):
            case 1:
                number = tmp[0]
            case 2:
                number, t = tmp
                try:
                    to_base = int(t)
                except ValueError:
                    print(f"invalid to_base: {t}")
                    continue
            case _:
                print("invalid input.")
                continue
        try:
            nn = cvtnum(number, to_base)
            print(nn)
        except ValueError as e:
            print(f"Error: {e}")
