"""Crypt-File 文件加密工具

个人所有的一些隐私文件有加密的需求，但是常见的加密工具要么不好用，要么速度慢，要么不安全（😀）。
根据实际情况取舍，选择了快速、好用、相对安全几个方面作为准则，开发了这个工具。

## 基本原理

基于随机字节串的循环异或加密对文件头和文件名进行加密替换。

1. 设置一个种子生成自定义 base64 码表
2. 生成随机字节串作为加密密钥 `key`
3. 读取文件头 4KB 数据进行异或加密替换并写入替换，文件小于 4KB 的完全加密
4. 文件名异或加密之后使用 base64 编码，然后与 key 用点连接作为新文件名

解密过程相反。

注意：
- 种子要保持稳定，否则可能丢失文件
- 本程序仅限个人使用，不要传播，毕竟加密算法很弱
- 不要用于重要文件
"""

import base64
import random
import string
from hashlib import sha256
from itertools import cycle, starmap
from operator import xor
from pathlib import Path

from ._common import glob_paths

SEED = "cfk"

# A-Za-z0-9
AB_D = string.ascii_uppercase + string.ascii_lowercase + string.digits


class MyBase64:
    def __init__(self, seed: str | None = None):
        self.__altchars = b"-_"
        chars = AB_D + self.__altchars.decode()
        my_chars = list(chars)

        if seed is None:
            seed = SEED

        old_state = random.getstate()
        random.seed(sha256(seed.encode()).digest())
        random.shuffle(my_chars)
        random.setstate(old_state)

        self.__trans_table_e = {ord(std): my for std, my in zip(chars, my_chars)}
        self.__trans_table_d = {ord(my): std for std, my in zip(chars, my_chars)}

    def encode(self, data: bytes) -> str:
        return (
            base64.b64encode(data, altchars=self.__altchars)
            .decode()
            .rstrip("=")
            .translate(self.__trans_table_e)
        )

    def decode(self, data: str) -> bytes:
        x = data.translate(self.__trans_table_d).encode()
        # 3个8比特分成4个6比特
        # 去除结尾的=剩余长度一定是 4n 4n-1 4n-2
        # 也就是 4n 4n+3 4n+2
        match len(x) % 4:
            case 0:
                pass
            case 3:
                x += b"="
            case 2:
                x += b"=="
            case 1:
                raise ValueError("invalid base64 string")
        return base64.b64decode(x, altchars=self.__altchars, validate=True)


def _xor_bytes(b: bytes, k: bytes) -> bytes:
    return bytes(starmap(xor, zip(b, cycle(k))))


BLOCK_SIZE = 1 << 12  # 4KB


def _replace_file_head(path: Path, key: bytes) -> None:
    with path.open("rb+") as fp:
        data = _xor_bytes(fp.read(BLOCK_SIZE), key)
        fp.seek(0)
        fp.write(data)


def _random_key() -> bytes:
    bs = random.choices(AB_D.encode(), k=random.randint(4, 8))
    return bytes(bs)


def _get_encrypt_name(
    name: str,
    key: bytes,
    *,
    b64: MyBase64,
) -> str:
    n = _xor_bytes(name.encode(), key)
    n = b64.encode(n)
    return f"{n}.{key.decode()}"


def _parse_encrypt_name(name: str, *, b64: MyBase64) -> tuple[str, bytes]:
    tmp = name.rsplit(".", 1)
    if len(tmp) == 1 or tmp[0] == "":
        raise ValueError(f"invalid encrypt name: {name}")

    n, key = tmp
    n = b64.decode(n)
    key = key.encode()

    return _xor_bytes(n, key).decode(), key


def encrypt_file(path: Path, b64: MyBase64) -> Path | None:
    key = _random_key()
    new_name = _get_encrypt_name(path.name, key, b64=b64)
    new_path = path.with_name(new_name)
    _replace_file_head(path, key)
    path.rename(new_path)
    return new_path


def decrypt_file(path: Path, b64: MyBase64) -> Path | None:
    new_name, key = _parse_encrypt_name(path.name, b64=b64)
    new_path = path.with_name(new_name)
    _replace_file_head(path, key)
    path.rename(new_path)
    return new_path


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("path", nargs="+", help="file/path, glob supported")
    parser.add_argument("--seed", help="seed for base64 table")

    cmd_grp = parser.add_mutually_exclusive_group(required=True)
    cmd_grp.add_argument("-e", "--encrypt", action="store_true", help="encrypt file")
    cmd_grp.add_argument("-d", "--decrypt", action="store_true", help="decrypt file")
    cmd_grp.add_argument("-g", "--glob", action="store_true", help="glob pattern")

    args = parser.parse_args()
    # print(args)

    paths = glob_paths(args.path)
    paths = map(Path, paths)

    if args.glob:
        for path in paths:
            print(path)
        return

    b64 = MyBase64(args.seed)
    fn = encrypt_file if args.encrypt else decrypt_file
    for path in paths:
        try:
            new_name = fn(path, b64)
        except Exception as e:
            print(f"[ERROR] {e}")
            continue
        if new_name is None:
            continue
        print(f"[OK] {path} => {new_name}")
