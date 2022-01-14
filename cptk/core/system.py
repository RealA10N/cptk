import sys
import subprocess
from typing import Union, Optional

from click import echo, prompt, style, Abort

from cptk.utils import cptkException


class SystemRunError(cptkException):
    """ Raised by System.run if something goes wrong. """


class SystemAbort(cptkException):
    """ Raised by the system if some internal process requests to abort. """


class System:

    CMD = lambda s: style(s, fg='yellow')
    ERROR = lambda s: style(s, bg='red', bold=True)
    WARN = lambda s: style(s, bg='yellow', fg='black', bold=True)

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
            echo(cls.CMD(cmd))

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
        echo(cls.ERROR(' ERROR ') + ' ' + error)

    @classmethod
    def unexpected_error(cls, error: Exception) -> None:

        msg = cls._expection_to_msg(error)
        echo(cls.ERROR(' UNEXPECTED ERROR ') + ' ' + msg)

        tb = error.__traceback__
        while tb is not None:
            file = tb.tb_frame.f_code.co_filename
            lineno = tb.tb_lineno
            echo('Inside ' + cls.CMD(f'{file}:{lineno}'))
            tb = tb.tb_next

    @classmethod
    def warn(cls, msg: str) -> None:
        echo(cls.WARN(' WARNING ') + ' ' + msg)

    @classmethod
    def ask(cls, question: str, options: dict) -> bool:
        res = prompt(cls.CMD(question)).strip()
        while res not in options:
            res = prompt(cls.CMD(question)).strip()
        return options[res]

    @classmethod
    def abort(cls):
        raise Abort
