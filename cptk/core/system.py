import sys
import subprocess

from typing import Union


class System:

    CMD = '\u001b[33m'      # yellow
    ERROR = '\u001b[41;1m'  # red bg, bold
    RESET = '\u001b[0m'

    _verbose = False  # not verbose by default

    @classmethod
    def run(cls, cmd: str) -> subprocess.CompletedProcess:

        if cls._verbose:
            print(cls.CMD + cmd + cls.RESET)

        return subprocess.run(
            cmd.split(),
            stdout=sys.stdout if cls._verbose else subprocess.PIPE,
            stderr=sys.stderr if cls._verbose else subprocess.PIPE,
        )

    @classmethod
    def set_verbosity(cls, v: bool) -> None:
        cls._verbose = v

    @staticmethod
    def _expection_to_msg(error: Exception) -> str:
        return ' '.join(error.args)

    @classmethod
    def error(cls, error: Union[str, Exception]) -> None:
        if isinstance(error, Exception):
            error = cls._expection_to_msg(error)
        print(f'{cls.ERROR} ERROR {cls.RESET} {error}')

    @classmethod
    def unexpected_error(cls, error: Union[str, Exception]) -> None:
        if isinstance(error, Exception):
            error = cls._expection_to_msg(error)
        print(f'{cls.ERROR} UNEXPECTED ERROR {cls.RESET} {error}')
