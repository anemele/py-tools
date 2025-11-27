"""Python Install Scripts"""

import platform
import shutil
import tomllib
from pathlib import Path
from typing import Mapping, Sequence

PY_SCRIPT_INSTALL_PATH = Path.home().joinpath("bin/pyins")
PY_SCRIPT_INSTALL_PATH.mkdir(exist_ok=True)

# I do not know OS other than Linux, so set all as `"bin", ""`
(BIN, EXE) = ("Scripts", ".exe") if platform.system() == "Windows" else ("bin", "")


def get_scripts_from_pyproject(project_path: Path) -> Sequence[Path]:
    content = project_path.joinpath("pyproject.toml").read_text(encoding="utf-8")
    scripts: Mapping[str, str] = tomllib.loads(content)["project"]["scripts"]
    names = scripts.keys()
    bin_path = project_path.joinpath(f".venv/{BIN}")
    scripts_path = [bin_path / f"{name}{EXE}" for name in names]
    return scripts_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("-s", "--skip-existing", action="store_true", default=False)

    args = parser.parse_args()
    project_path: Path = args.project_path
    skip_existing: bool = args.skip_existing

    if not project_path.exists():
        print("not found project.toml")
        return

    try:
        scripts = get_scripts_from_pyproject(project_path)
    except FileNotFoundError:
        print("not found pyproject.toml")
        return
    except tomllib.TOMLDecodeError:
        print("failed to decode pyproject.toml")
        return
    except KeyError:
        print("no scripts found in pyproject.toml")
        return

    print(f"Installing Python scripts ({PY_SCRIPT_INSTALL_PATH})\n")
    print(f"  {project_path.resolve()} ({len(scripts)})\n")
    for script_path in scripts:
        # TODO: check if script already exists?
        if skip_existing and script_path.exists():
            print(f"  - {script_path.name} (exists, skip)")
            continue

        try:
            shutil.copy(script_path, PY_SCRIPT_INSTALL_PATH)
            print(f"  + {script_path.name}")
        except PermissionError:
            print(f"  x {script_path.name} (permission denied)")
