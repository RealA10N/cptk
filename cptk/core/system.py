import sys
import subprocess

from typing import Union, Optional

from cptk.utils import cptkException


class SystemRunError(cptkException):
    """ Raised by System.run if something goes wrong. """


class System:

    CMD = '\u001b[33m'      # yellow
    ERROR = '\u001b[41;1m'  # red bg, bold
    RESET = '\u001b[0m'

    _verbose = None

    @classmethod
    def run(cls,
            cmd: str,
            errormsg: str = None,
            verbose: bool = None,
            ) -> subprocess.CompletedProcess:
        """ Runs the given command in the terminal. If 'errormsg' is provided,
        asserts that the returncode from the process is zero, and if not, raises
        an SystemRunError with the given message. If 'verbose' is provided, it
        overwrites the classes verbosity setting. """

        if verbose is None:
            verbose = cls._verbose

        if verbose:
            print(cls.CMD + cmd + cls.RESET)

        res = subprocess.run(
            cmd.split(),
            stdout=sys.stdout if verbose else subprocess.PIPE,
            stderr=sys.stderr if verbose else subprocess.PIPE,
        )

        if errormsg is not None and res.returncode != 0:
            raise SystemRunError(errormsg)

        return res

    @classmethod
    def set_verbosity(cls, v: Optional[bool]) -> None:
        """ Verbosity can be True, False, or None (which means "defalt"). """
        cls._verbose = v

    @classmethod
    def get_verbosity(cls) -> Optional[bool]:
        return cls._verbose

    @staticmethod
    def _expection_to_msg(error: Exception) -> str:
        return ' '.join(str(a) for a in error.args)

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
