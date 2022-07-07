#!/usr/bin/env python

from importlib import import_module
import json
import pathlib
import sys
from typing import Dict


def load_parameter_generators():
    for project in pathlib.Path("projects").iterdir():
        generator_file = project / "scripts" / "parameters_generator.py"
        if not generator_file.exists():
            continue
        module_name = str(generator_file).replace("/", ".").replace(".py", "")
        module = import_module(module_name)
        if "generate_parameters" not in dir(module):
            print(
                f"Skipping module {module_name}, no 'generate_parameters' function found")
            continue
        yield module


def generate_parameters() -> Dict:
    # TODO: Here we'll have tons of different conditionals to understand
    # what is actually happening.
    # Given that information we can generate the correct parameters for
    # workflows/jobs we must run.
    parameters_by_module = {
        # Root parameters
        __name__: {
            "should_it_run": True,
            "test": {
                "data": True
            }
        }
    }

    for module in load_parameter_generators():
        params = module.generate_parameters()
        # Check for duplicate keys
        for (other_module, other_params) in parameters_by_module.items():
            diff = params.keys() & other_params.keys()
            if len(diff) > 0:
                identical_params = ", ".join(diff)
                sys.exit(
                    f"Identical parameters {identical_params} found both in {module.__name__} and {other_module}")
        # If all parameters are unique keep going
        parameters_by_module[module.__name__] = params

    res = {}
    for params in parameters_by_module.values():
        res.update(params)

    return res


if __name__ == "__main__":
    print(json.dumps(generate_parameters()))
