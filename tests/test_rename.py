from pathlib import Path

import pytest

from py_tools.rename import dispatch


def test_dispatch():
    assert dispatch("lower")(Path("a/b/aBs.Txt")) == Path("a/b/abs.txt")
    assert dispatch("upper")(Path("a/b/aBs.Txt")) == Path("a/b/ABS.TXT")

    assert dispatch("no-ext")(Path("a/b/c.txt")) == Path("a/b/c")
    assert dispatch("no-ext")(Path("a/b/c")) == Path("a/b/c")

    assert dispatch("s/c/d/")(Path("a/b/c.txt")) == Path("a/b/d.txt")
    assert dispatch("s/c/d/")(Path("a/b/c")) == Path("a/b/d")
    assert dispatch("s/c/d/")(Path("a/b/c/d.txt")) == Path("a/b/c/d.txt")

    assert dispatch("s/^/x/")(Path("a/b/c.txt")) == Path("a/b/xc.txt")
    assert dispatch("s/$/x/")(Path("a/b/c.txt")) == Path("a/b/cx.txt")
    assert dispatch("s/^x//")(Path("a/b/xc.txt")) == Path("a/b/c.txt")
    assert dispatch("s/x$//")(Path("a/b/cx.txt")) == Path("a/b/c.txt")

    assert dispatch(r"s/\d//")(Path("a/b/abc123def.txt")) == Path("a/b/abcdef.txt")
    assert dispatch("s/[A-Za-z]/-/")(Path("a/b/123abc.txt")) == Path("a/b/123---.txt")

    with pytest.raises(ValueError, match="not match s/str/repl/"):
        dispatch("s/")
        dispatch("s//")
        dispatch("s/abc/")
        dispatch("s/abc/def")

    with pytest.raises(ValueError, match="invalid reg expr"):
        dispatch("s/[a-z//")
        dispatch(r"s/*//")
