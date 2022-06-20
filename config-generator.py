#!/usr/bin/env python

import pathlib
import subprocess
import sys
from typing import List


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
        raise res.stderr


def merge_config_files(configs: List[pathlib.Path]) -> bytes:
    # Copy the files into the .circleci folder here.

    # Create a mapping between the original file and the copied one,
    # this should ease error reporting.

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
