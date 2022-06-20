#!/usr/bin/env python

import pathlib
import subprocess
from shutil import copytree
from typing import Dict, List


def validate_config(circleci_cli: str, config: bytes):
    res = subprocess.run(
        [circleci_cli, "config", "validate", "-"],
        input=config,
        capture_output=True
    )
    if res.returncode:
        raise Exception(res.stderr.decode("utf-8"))


def find_configs() -> Dict[str, List[pathlib.Path]]:
    # TODO: This is not used now but it can be useful for linting.
    # I'll leave it here.
    res = {}
    for project in pathlib.Path("projects").iterdir():
        configs = project.glob(".circleci/**/*.yml")
        res[project.name] = list(configs)
    return res


def merge_config_files(circleci_cli: str) -> bytes:
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
        [circleci_cli, "config", "pack", ".circleci/continue"],
        capture_output=True
    )

    return res.stdout


def generate_config(circleci_cli: str):
    generated = merge_config_files(circleci_cli)

    try:
        validate_config(circleci_cli, generated)
    except Exception as e:
        sys.exit(f"Config validation failed after merging: {e}")

    return generated.decode("utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--circleci-cli", type=str, default="circleci",
                        help="Path to CircleCI CLI")

    args = parser.parse_args()

    config = generate_config(args.circleci_cli)

    print(config)
