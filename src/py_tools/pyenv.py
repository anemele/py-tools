#!/usr/bin/env python3.12
"""Python envs manager.

Wrapper of external programs.
Make sure `uv` is installed and in PATH.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

# where to store python envs
ROOT_PATH = Path.home() / ".pyenvs"
ROOT_PATH.mkdir(exist_ok=True)

# prefix of virtual envs
ENV_PREFIX = "env-"


def _validate_env(env_path: Path) -> bool:
    return (env_path / "pyproject.toml").exists()


def cmd_list():
    print(f"List envs in {ROOT_PATH}")
    for env in ROOT_PATH.glob(f"{ENV_PREFIX}*"):
        if not _validate_env(env):
            print(f"WARNING: {env} is not a valid pyenv.")
            continue
        name = env.name.removeprefix(ENV_PREFIX)
        print(f"  {name}")


def cmd_run(name: str, *args):
    env_path = ROOT_PATH / f"{ENV_PREFIX}{name}"
    if not _validate_env(env_path):
        print(f"ERROR: {name} is not a valid pyenv.")
        return
    subprocess.run(args, cwd=env_path, shell=True)


def cmd_tree(name: str, depth: int = 1):
    cmd_run(name, "uv", "tree", "--depth", str(depth))


def cmd_add(name: str, *pkg: str):
    cmd_run(name, "uv", "add", *pkg)


def cmd_remove(name: str, *pkg: str):
    cmd_run(name, "uv", "remove", *pkg)


def cmd_sync(name: str):
    cmd_run(name, "uv", "sync")


def cmd_create(name: str, python: Optional[str] = None):
    env_path = ROOT_PATH / f"{ENV_PREFIX}{name}"
    if env_path.exists():
        print(f"ERROR: {name} already exists.")
        return
    cmd = ["uv", "init", str(env_path)]
    if python is not None:
        cmd.extend(["--python", python])
    subprocess.run(cmd)


def cmd_drop(name: str):
    env_path = ROOT_PATH / f"{ENV_PREFIX}{name}"
    if not _validate_env(env_path):
        print(f"ERROR: {name} is not a valid pyenv.")
        return
    try:
        shutil.rmtree(env_path)
        print(f"Dropped {name}.")
    except OSError as e:
        print(f"ERROR: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    _list_parser = subparsers.add_parser("list", help="List all pyenvs.")

    tree_parser = subparsers.add_parser("tree", help="Show dependency tree of a pyenv.")
    tree_parser.add_argument("name", help="Name of the pyenv.")
    tree_parser.add_argument(
        "-d", "--depth", type=int, default=1, help="Depth of the tree."
    )

    add_parser = subparsers.add_parser("add", help="Add packages to a pyenv.")
    add_parser.add_argument("name", help="Name of the pyenv.")
    add_parser.add_argument("pkg", nargs="+", help="Packages to add.")

    remove_parser = subparsers.add_parser(
        "remove", help="Remove packages from a pyenv."
    )
    remove_parser.add_argument("name", help="Name of the pyenv.")
    remove_parser.add_argument("pkg", nargs="+", help="Packages to remove.")

    sync_parser = subparsers.add_parser("sync", help="Sync packages in a pyenv.")
    sync_parser.add_argument("name", help="Name of the pyenv.")

    create_parser = subparsers.add_parser("create", help="Create a new pyenv.")
    create_parser.add_argument("name", help="Name of the pyenv.")
    create_parser.add_argument(
        "-p",
        "--python",
        help="Python version to use for the pyenv. (default: system default)",
    )

    drop_parser = subparsers.add_parser("drop", help="Delete a pyenv.")
    drop_parser.add_argument("name", help="Name of the pyenv.")

    run_parser = subparsers.add_parser("run", help="Run a command in a pyenv.")
    run_parser.add_argument("name", help="Name of the pyenv.")
    run_parser.add_argument("args", nargs="...", help="Command arguments.")

    args = parser.parse_args()
    # print(args)
    # return

    match args.cmd:
        case "list":
            cmd_list()
        case "tree":
            cmd_tree(args.name, args.depth)
        case "add":
            cmd_add(args.name, *args.pkg)
        case "remove":
            cmd_remove(args.name, *args.pkg)
        case "sync":
            cmd_sync(args.name)
        case "create":
            cmd_create(args.name, args.python)
        case "drop":
            cmd_drop(args.name)
        case "run":
            cmd_run(args.name, *args.args)
        case _:
            # should never happen
            print(f"ERROR: unknown command {args.cmd}")
