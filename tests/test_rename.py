from pathlib import Path

import pytest

from py_tools.rename import wrap


def test_wrap():
    assert wrap("lower")(Path("a/b/aBs.Txt")) == Path("a/b/abs.txt")
    assert wrap("upper")(Path("a/b/aBs.Txt")) == Path("a/b/ABS.TXT")

    assert wrap("no-ext")(Path("a/b/c.txt")) == Path("a/b/c")
    assert wrap("no-ext")(Path("a/b/c")) == Path("a/b/c")

    assert wrap("s/c/d/")(Path("a/b/c.txt")) == Path("a/b/d.txt")
    assert wrap("s/c/d/")(Path("a/b/c")) == Path("a/b/d")
    assert wrap("s/c/d/")(Path("a/b/c/d.txt")) == Path("a/b/c/d.txt")

    assert wrap("s/^/x/")(Path("a/b/c.txt")) == Path("a/b/xc.txt")
    assert wrap("s/$/x/")(Path("a/b/c.txt")) == Path("a/b/cx.txt")
    assert wrap("s/^x//")(Path("a/b/xc.txt")) == Path("a/b/c.txt")
    assert wrap("s/x$//")(Path("a/b/cx.txt")) == Path("a/b/c.txt")

    assert wrap(r"s/\d//")(Path("a/b/abc123def.txt")) == Path("a/b/abcdef.txt")
    assert wrap("s/[A-Za-z]/-/")(Path("a/b/123abc.txt")) == Path("a/b/123---.txt")

    with pytest.raises(ValueError, match="not match s/str/repl/"):
        wrap("s/")
        wrap("s//")
        wrap("s/abc/")
        wrap("s/abc/def")

    with pytest.raises(ValueError, match="invalid reg expr"):
        wrap("s/[a-z//")
        wrap(r"s/*//")
