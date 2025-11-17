"""中华人民共和国居民身份证号码工具。

- 输入 15 位一代号码返回 18 位二代号码
- 输入 17 位二代号码返回 18 位二代号码
- 输入 18 位号码验证，失败则返回正确的 18 位号码

注意：不验证籍贯、年龄等信息，仅验证校验位。
"""

COEFFICIENT = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
LAST_NUMBER = "10X987654321"


def calculate_check_digit(id17: str) -> str:
    """计算校验位。
    输入 17 位纯数字。
    """
    s = sum(int(x) * c for x, c in zip(id17, COEFFICIENT))
    return LAST_NUMBER[s % 11]


def cvt_17_to_18(id17: str) -> str:
    """将 17 位二代号码转换为 18 位二代号码。"""
    check_digit = calculate_check_digit(id17)
    return id17 + check_digit


def validate_18(id18: str) -> str:
    """验证 18 位号码是否正确。"""
    n18 = calculate_check_digit(id18[:17])
    ssn = id18[:17] + n18
    if n18 == id18[17].upper():
        return ssn
    return f"校验位错误，正确的号码是 {ssn}"


def cvt_15_to_18(id15: str) -> str:
    """将 15 位一代号码转换为 18 位二代号码。
    一般认为一代号码都是 19XX 年出生的。"""
    id17 = id15[:6] + "19" + id15[6:]
    return cvt_17_to_18(id17)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("id", help="15/17/18 位居民身份证号码")

    args = parser.parse_args()
    ssn: str = args.id.strip()

    if not ssn[:17].isdigit():
        print("前 17 位号码必须是纯数字")
        return
    match len(ssn):
        case 15:
            print(cvt_15_to_18(ssn))
        case 17:
            print(cvt_17_to_18(ssn))
        case 18:
            print(validate_18(ssn))
        case _:
            print("输入的号码长度必须是 15/17/18 位")
