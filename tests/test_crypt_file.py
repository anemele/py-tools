from hashlib import file_digest, sha256
from pathlib import Path

import pytest

from py_tools.crypt_file import (
    MyBase64,
    _get_encrypt_name,
    _parse_encrypt_name,
    decrypt_file,
    encrypt_file,
)


def test_MyBase64():
    my_base64 = MyBase64()
    sample = b"hello base64"

    for i in range(len(sample)):
        data = sample[:i]
        encoded = my_base64.encode(data)
        print(encoded)
        assert not encoded.endswith("=")
        assert my_base64.decode(encoded) == data


def test_x_encrypt_name():
    B64 = MyBase64("seed")
    NAME = "ABCDEFG"
    KEY = b"key"
    ENAME = "0hBPId5jI5.key"

    ename = _get_encrypt_name(NAME, KEY, b64=B64)
    assert ename == ENAME

    dname, key = _parse_encrypt_name(ename, b64=B64)
    assert dname == NAME
    assert key == KEY

    with pytest.raises(ValueError, match="invalid encrypt name"):
        _parse_encrypt_name(".gitignore", b64=B64)

    BAD_B64 = MyBase64("bad_seed")
    with pytest.raises(UnicodeDecodeError):
        _parse_encrypt_name(ename, b64=BAD_B64)


def test_real():
    b64 = MyBase64("random-seed")
    paths = Path(__file__).with_suffix("").glob("*")

    count = 0
    for path in paths:
        count += 1

        with path.open("rb") as fp:
            old_hash = file_digest(fp, sha256).hexdigest()

        tmp_path = encrypt_file(path, b64)
        assert tmp_path is not None

        new_path = decrypt_file(tmp_path, b64)
        assert new_path is not None
        assert new_path.name == path.name

        with new_path.open("rb") as fp:
            new_hash = file_digest(fp, sha256).hexdigest()
        assert new_hash == old_hash

    assert count > 0
