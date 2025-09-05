from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Final


MYPY_VERSION_FILE: Final = "mypy/mypy/version.py"
ALPHA: Final = "a"
BETA: Final = "b"


def read_mypy_version_from_file() -> str:
    content = Path(MYPY_VERSION_FILE).read_text().splitlines()
    version_line = [line for line in content if line.startswith("__version__")][0]
    version = version_line.partition(" = ")[2].strip('"').removesuffix("+dev")
    return version


def read_existing_tags(prefix: str | None = None) -> list[str]:
    proc = subprocess.run(shlex.split("git tag --list"), capture_output=True)
    stdout = sorted(proc.stdout.decode().splitlines())
    if prefix is not None:
        return [item for item in stdout if item.startswith(prefix)]
    return stdout


def find_next_version(version: str, tags: list[str], beta: bool = False) -> str:
    match tags:
        case [*_, last_release]:
            last_suffix = last_release.removeprefix(version)
            pre, v = re.match(r"(\w)(\d+)", last_suffix).groups()
            v = int(v) + 1
        case _:
            pre = ALPHA
            v = 1
    if beta and pre == ALPHA:
        pre = BETA
        v = 1
    return f"{version}{pre}{v}"


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--beta", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    version = read_mypy_version_from_file()
    # version = "1.9.0"
    version = "1.18.0"
    # version = "1.19.0"
    tags = read_existing_tags(version)
    # print(tags)
    next_version = find_next_version(version, tags, args.beta)
    print(next_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
