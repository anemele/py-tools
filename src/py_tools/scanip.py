"""LAN IP scanner (support IPv4 only)"""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_network
from typing import Iterable


def get_net_ip_list(address: str) -> Iterable[str]:
    try:
        network = ip_network(address, strict=False)
        hosts = network.hosts()
        yield from map(str, hosts)
    except Exception:
        pass


def gen_local_ip_list():
    import socket

    local_ip = socket.gethostbyname(socket.gethostname())
    return get_net_ip_list(f"{local_ip}/24")


def _ping_ip(ip: str) -> str | None:
    res = subprocess.run(["ping", ip], capture_output=True).stdout
    idx = res.lower().find(b"ttl=")
    if idx >= 0:
        return ip


def ping_ip_list(ip_list: Iterable[str]) -> None:
    with ThreadPoolExecutor(max_workers=64) as executor:
        results = executor.map(_ping_ip, ip_list)
        count = 0
        ok = 0
        for ip in results:
            count += 1
            if ip is not None:
                ok += 1
                print(ip)
    print(f"{ok}/{count}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ip_address", nargs="*")

    args = parser.parse_args()
    ip_address_list: list[str] = args.ip_address

    if len(ip_address_list) == 0:
        ip_list = gen_local_ip_list()
    else:
        from itertools import chain

        ip_list = chain.from_iterable(map(get_net_ip_list, ip_address_list))

    ping_ip_list(ip_list)
