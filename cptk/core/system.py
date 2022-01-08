import sys
import subprocess


class System:

    CMD = '\u001b[33m'
    RESET = '\u001b[0m'

    _verbose = False  # not verbose by default

    @classmethod
    def run(cls, cmd: str) -> None:

        if cls._verbose:
            print(cls.CMD + cmd + cls.RESET)

        subprocess.run(
            cmd.split(),
            stdout=sys.stdout if cls._verbose else None,
            stderr=sys.stderr if cls._verbose else None,
        )

    @classmethod
    def set_verbosity(cls, v: bool) -> None:
        cls._verbose = v
