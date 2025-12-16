import sys
from pathlib import Path

import pytest

from py_tools.rename import main, rename_convert, rename_substitute


def test_cli(capsys: pytest.CaptureFixture):
    test_file = Path(__file__)

    sys.argv[1:] = ["-s", r"(?<=test)_\w+", "_ok", __file__, "--dry-run"]
    expected = test_file.with_stem("test_ok")
    exit_code = main()
    assert not exit_code
    captured = capsys.readouterr()
    assert captured.out.strip() == f"[DRY-RUN] {test_file} -> {expected}"
    assert captured.err.strip() == ""

    sys.argv[1:] = ["-t", "swap", __file__, "--dry-run"]
    expected = test_file.with_name(test_file.name.swapcase())
    exit_code = main()
    assert not exit_code
    captured = capsys.readouterr()
    assert captured.out.strip() == f"[DRY-RUN] {test_file} -> {expected}"
    assert captured.err.strip() == ""


def test_convert():
    assert rename_convert("lower")(Path("a/b/aBs.Txt")) == Path("a/b/abs.txt")
    assert rename_convert("upper")(Path("a/b/aBs.Txt")) == Path("a/b/ABS.TXT")
    assert rename_convert("swap")(Path("a/b/aBs.Txt")) == Path("a/b/AbS.tXT")
    assert rename_convert("caps")(Path("a/b/aBs.Txt")) == Path("a/b/ABs.Txt")
    assert rename_convert("title")(Path("a/b/aBs-abc_def.txt")) == Path(
        "a/b/ABs-Abc_def.Txt"
    )

    assert rename_convert("no-ext")(Path("a/b/c.txt")) == Path("a/b/c")
    assert rename_convert("no-ext")(Path("a/b/c")) == Path("a/b/c")


def test_substitute():
    assert rename_substitute(("c", "d"))(Path("a/b/c.txt")) == Path("a/b/d.txt")
    assert rename_substitute(("c", "d"))(Path("a/b/c")) == Path("a/b/d")
    assert rename_substitute(("c", "d"))(Path("a/b/c/d.txt")) == Path("a/b/c/d.txt")

    assert rename_substitute(("^", "x"))(Path("a/b/c.txt")) == Path("a/b/xc.txt")
    assert rename_substitute(("$", "x"))(Path("a/b/c.txt")) == Path("a/b/cx.txt")
    assert rename_substitute(("^x", ""))(Path("a/b/xc.txt")) == Path("a/b/c.txt")
    assert rename_substitute(("x$", ""))(Path("a/b/cx.txt")) == Path("a/b/c.txt")

    assert rename_substitute((r"\d", ""))(Path("a/b/abc123def.txt")) == Path(
        "a/b/abcdef.txt"
    )
    assert rename_substitute(("[A-Za-z]", "-"))(Path("a/b/123abc.txt")) == Path(
        "a/b/123---.txt"
    )
