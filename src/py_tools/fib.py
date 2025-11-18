"""Fibonacci number calculator"""


def calc_fib(n: int) -> int:
    """Calculate Fibonacci sequence"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", type=int, help="n-th Fibonacci number")
    args = parser.parse_args()
    n = args.n
    if n <= 0:
        parser.error("n must be positive integer")
    print(calc_fib(n))
