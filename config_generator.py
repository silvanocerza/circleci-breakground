#!/usr/bin/env python

import pathlib
import subprocess
import sys
from shutil import copytree
from typing import Dict, List


def find_configs() -> List[pathlib.Path]:
    # TODO: Use various env things to determine which config files
    # we need to merge together

    # Probably we're gonna fake it for now
    # NOTE: Might be cool to have a lookup table to know which file is
    # necessary for whatever project.
    return []


def validate_config(config: bytes):
    res = subprocess.run(
        ["circleci", "config", "validate", "-"],
        input=config
    )
    if res.returncode:
        raise Exception(res.stderr.decode("utf-8"))


def find_config_files() -> Dict[str, List[pathlib.Path]]:
    # TODO: This is not used now but it can be useful for linting.
    # I'll leave it here.
    res = {}
    for project in pathlib.Path("projects").iterdir():
        configs = project.glob(".circleci/**/*.yml")
        res[project.name] = list(configs)
    return res


def merge_config_files() -> bytes:
    # TODO: Probably we should enforce the naming projects' configs.
    # <project_name>/.circleci/jobs/@<project_name>.yml should work.

    # Copy the files into the global .circleci folder
    for project in pathlib.Path("projects").iterdir():
        project_configs = project / ".circleci"
        if not project_configs.exists():
            continue
        copytree(project_configs, pathlib.Path(
            ".circleci", "continue"), dirs_exist_ok=True)

    # IMPORTANT: Verify that top level keys are not duplicated in different files
    # in the same folder, that's a big no-no since keys are overwritten
    # with no warning.

    res = subprocess.run(
        ["circleci", "config", "pack", ".circleci/continue"],
        capture_output=True
    )

    return res.stdout


def generate_config():
    configs = find_configs()
    try:
        validate_config(configs)
    except Exception as e:
        sys.exit(f"Config validation failed before merging: {e}")

    generated = merge_config_files(configs)

    try:
        validate_config([generated])
    except Exception as e:
        sys.exit(f"Config validation failed after merging: {e}")

    return generated.decode("utf-8")


if __name__ == "__main__":
    config = generate_config()

    print(config)
