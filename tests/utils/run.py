from __future__ import annotations

import subprocess


def run(cmd: str) -> subprocess.CompletedProcess:
    """ Runs the given commend in the terminal and returns the completed
    process instance that represents the process. """
    return subprocess.run(cmd.split())
