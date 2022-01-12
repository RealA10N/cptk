import sys
import subprocess

from typing import Union, Optional

from cptk.utils import cptkException


class SystemRunError(cptkException):
    """ Raised by System.run if something goes wrong. """


class SystemAbort(cptkException):
    """ Raised by the system if some internal process requests to abort. """


class System:

    CMD = '\u001b[33m'      # yellow
    ERROR = '\u001b[41;1m'  # red bg, bold
    WARN = '\u001b[43;30;1m'  # orange bg, black fg, bold
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
        return ', '.join(str(a) for a in error.args)

    @classmethod
    def error(cls, error: Union[str, Exception]) -> None:
        if isinstance(error, Exception):
            error = cls._expection_to_msg(error)
        print(f'{cls.ERROR} ERROR {cls.RESET} {error}')

    @classmethod
    def unexpected_error(cls, error: Exception) -> None:

        msg = cls._expection_to_msg(error)
        print(f'{cls.ERROR} UNEXPECTED ERROR {cls.RESET} {msg}')

        tb = error.__traceback__
        while tb is not None:
            file = tb.tb_frame.f_code.co_filename
            lineno = tb.tb_lineno

            print(f'Inside {cls.CMD}{file}:{lineno}{cls.RESET}')
            tb = tb.tb_next

    @classmethod
    def warn(cls, msg: str) -> None:
        print(f'{cls.WARN} WARNING {cls.RESET} {msg}')

    @classmethod
    def ask(cls, question: str, options: dict) -> bool:
        res = input(f'{cls.CMD}{question}{cls.RESET} ').strip()
        while res not in options:
            res = input(f'{cls.CMD}{question}{cls.RESET} ').strip()
        return options[res]

    @classmethod
    def abort(cls):
        raise SystemAbort
