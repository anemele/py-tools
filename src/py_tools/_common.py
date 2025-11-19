"""Common utilities."""


def human_readable_size(size_of_bytes: int) -> str:
    carry = 1024
    if size_of_bytes < carry:
        return f"{size_of_bytes} B"
    size = size_of_bytes
    for u in "KMGTPEZYBND":
        size /= carry
        if size < carry:
            return f"{size:.2f} {u}B"
    return f"{size:.2f} CB"
