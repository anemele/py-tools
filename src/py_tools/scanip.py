"""LAN IP scanner (support IPv4 only)"""

import platform
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_network
from typing import Iterable

import psutil


def get_local_ip():
    addrs = psutil.net_if_addrs()
    for if_name, if_addrs in addrs.items():
        # only WLAN
        if not if_name.lower().startswith("wlan"):
            continue

        for addr in if_addrs:
            if addr.family == socket.AF_INET:  # IPV4
                data = dict(if_name=if_name, ip_addr=addr.address)
                yield data


def get_net_ip_list(address: str) -> Iterable[str]:
    try:
        network = ip_network(address, strict=False)
        hosts = network.hosts()
        yield from map(str, hosts)
    except Exception:
        pass


def gen_local_ip_list():
    for data in get_local_ip():
        print(data)
        local_ip = data["ip_addr"]
        break
    else:
        local_ip = socket.gethostbyname(socket.gethostname())
        print(local_ip)
    return get_net_ip_list(f"{local_ip}/24")


if platform.system() == "Windows":
    PING_CMD = "ping -n 2 -w 1000"
else:
    PING_CMD = "ping -c 2 -W 1000"


def is_host_up(ip: str) -> str | None:
    cmd = f"{PING_CMD} {ip}".split()
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return ip
    except Exception:
        pass
    return None


def scan_with_ping(ips_to_scan: Iterable[str], max_workers: int = 50):
    print(f"\nping scanning ... ({max_workers=})")

    count = 0
    count_active = 0

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(is_host_up, ips_to_scan)

    for ip in results:
        count += 1
        if ip is not None:
            count_active += 1
            print(f"+ {ip}")

    end_time = time.perf_counter()
    cost_time = end_time - start_time

    print(f"\n{count_active}/{count} cost {cost_time:.2f} s")


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

    scan_with_ping(ip_list)
