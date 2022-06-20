#!/usr/bin/env python

import json
from typing import Dict


def generate_parameters() -> Dict:
    # TODO: Here we'll have tons of different conditionals to understand
    # what is actually happening.
    # Given that information we can generate the correct parameters for
    # workflows/jobs we must run.
    return {
        "should_it_run": True,
        "wakey_wakey": True,
    }


if __name__ == "__main__":
    print(json.dumps(generate_parameters()))
