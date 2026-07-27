"""
验证 18 位身份证号码，包括：

- 籍贯（省）
- 生年月日
- 校验码
"""

from datetime import datetime

COEFFICIENT = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
LAST_NUMBER = "10X987654321"
_PROVINCE_CODE = "11,12,13,14,15,21,22,23,31,32,33,34,35,36,37,41,42,43,44,45,46,50,51,52,53,54,61,62,63,64,65,71,81,82"
PROVINCE_CODE = {p for p in _PROVINCE_CODE.split(",")}


def calculate_check_digit(id17: str) -> str:
    """计算校验位。
    输入 17 位纯数字。
    """
    s = sum(int(x) * c for x, c in zip(id17, COEFFICIENT))
    return LAST_NUMBER[s % 11]


def validate_18(id18: str) -> None:
    if id18[:2] not in PROVINCE_CODE:
        raise ValueError(f"invalid province code: {id18[:2]}")

    try:
        datetime.strptime(id18[6:14], "%Y%m%d")
    except ValueError:
        raise ValueError(f"invalid date: {id18[6:14]}")

    n18 = calculate_check_digit(id18[:17])
    if n18 != id18[17].upper():
        raise ValueError(f"check code is {n18}, while got {id18[17]}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("id18", help="18 位居民身份证号码")

    args = parser.parse_args()
    ssn: str = args.id18.strip()

    if len(ssn) != 18:
        print("必须是 18 位")
        return
    if not ssn[:17].isdigit():
        print("前 17 位号码必须是纯数字")
        return

    try:
        validate_18(ssn)
        print("ok")
    except ValueError as e:
        print(e)
