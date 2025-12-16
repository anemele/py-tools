import sys

import pytest

from py_tools.numsys import NumeralSystem as NS
from py_tools.numsys import main


def test_cli(capsys: pytest.CaptureFixture):
    sys.argv[1:] = ["123", "2"]
    exit_code = main()
    assert not exit_code
    captured = capsys.readouterr()
    assert captured.out.strip() == "1111011_2"
    assert captured.err.strip() == ""

    sys.argv[1:] = ["1111011_2"]
    exit_code = main()
    assert not exit_code
    captured = capsys.readouterr()
    assert captured.out.strip() == "123_10"
    assert captured.err.strip() == ""


def test_exception():
    with pytest.raises(ValueError, match="at least 2"):
        NS("")
        NS("1")
        NS("好")
        NS(["1234"])

    with pytest.raises(ValueError, match="no-repeat"):
        NS("1213")
        NS("121")


def test_valid():
    # no prefix
    NS(["0", "10", "110", "1110"])

    # has prefix
    NS(["0", "1", "00", "01", "10", "11"])


def test_convert():
    ns = NS()
    assert ns.convert("520", 2) == "1000001000_2"
    assert ns.convert("ff_16", 10) == "255_10"
    assert ns.convert("abc_16", 10) == "2748_10"

    ns = NS("你好啊")
    assert ns.convert("你好啊_3", 2) == "好你好_2"
    assert ns.convert("啊你好_3", 2) == "好你你好好_2"

    import string

    ns = NS(string.digits + string.ascii_letters)
    assert ns.convert("abcdefg_50", 60) == "3prsRwK_60"
    assert ns.convert("3prsRwK_60", 50) == "abcdefg_50"


def test_any_to_int():
    assert NS("012")._any_to_int("100", 3) == 9
    assert NS("012")._any_to_int("100", 2) == 4
    assert NS("abcdef")._any_to_int("cba", 4) == 36


def test_int_to_any():
    assert NS("012")._int_to_any(9, 3) == "100"
    assert NS("012")._int_to_any(4, 2) == "100"
    assert NS("abcdef")._int_to_any(36, 4) == "cba"
