import sys
from typing import TYPE_CHECKING
from typing import Union

import colorama

from cptk.utils import cptkException

if TYPE_CHECKING:
    from subprocess import CompletedProcess


class SystemRunError(cptkException):
    """ Raised by System.run if something goes wrong. """


class System:

    CMD = colorama.Fore.YELLOW
    LOG = colorama.Fore.LIGHTBLACK_EX
    ERROR = colorama.Back.RED + colorama.Style.BRIGHT
    WARN = colorama.Back.YELLOW + colorama.Fore.BLACK + colorama.Style.BRIGHT
    RESET = colorama.Style.RESET_ALL

    _verbosity = 0
    _yes_stack = 0

    @classmethod
    def run(cls,
            cmd: str,
            errormsg: str = None,
            verbose: bool = None,
            ) -> 'CompletedProcess':
        """ Runs the given command in the terminal. If 'errormsg' is provided,
        asserts that the returncode from the process is zero, and if not,
        raises an SystemRunError with the given message. If 'verbose' is
        provided, it overwrites the classes verbosity setting. """

        import subprocess

        if verbose is None:
            verbose = cls._verbosity >= 2

        if verbose:
            cls.echo(cls.CMD + cmd + cls.RESET)

        res = subprocess.run(
            cmd.split(),
            check=False,
            stdout=sys.stdout if verbose else subprocess.PIPE,
            stderr=sys.stderr if verbose else subprocess.PIPE,
        )

        if errormsg is not None and res.returncode != 0:
            raise SystemRunError(errormsg)

        return res

    @classmethod
    def set_verbosity(cls, level: int = 0) -> None:
        """ Verbosity can be True, False, or None (which means "defalt"). """
        cls._verbosity = level

    @classmethod
    def set_yes(cls, amount: int = 1) -> None:
        cls._yes_stack = amount

    @classmethod
    def pop_yes(cls) -> bool:
        if cls._yes_stack > 0:
            cls._yes_stack -= 1
            return True
        return False

    @staticmethod
    def _expection_to_msg(error: Exception) -> str:
        return ', '.join(str(a) for a in error.args)

    @classmethod
    def error(cls, error: Union[str, Exception]) -> None:
        if isinstance(error, Exception):
            error = cls._expection_to_msg(error)

        cls.echo(f"{cls.ERROR} ERROR {cls.RESET} {error}")

    @classmethod
    def unexpected_error(cls, error: Exception) -> None:

        title = type(error).__name__
        desc = cls._expection_to_msg(error)
        msg = title if not desc else f'{title}: {desc}'

        cls.echo(f"{cls.ERROR} UNEXPECTED ERROR {cls.RESET} {msg}")

        tb = error.__traceback__
        while tb is not None:
            file = tb.tb_frame.f_code.co_filename
            lineno = tb.tb_lineno
            cls.echo(f'Inside {cls.CMD}{file}:{lineno}{cls.RESET}')
            tb = tb.tb_next

    @classmethod
    def abnormal_exit(cls) -> None:
        cls.echo(f"{cls.ERROR} ABNORMAL EXIT {cls.RESET}")

    @classmethod
    def warn(cls, msg: str) -> None:
        cls.echo(f"{cls.WARN} WARNING {cls.RESET} {msg}")

    @classmethod
    def confirm(cls, question: str) -> bool:
        if cls.pop_yes(): return True
        return cls.ask(question, {('Y', 'y'): True, ('n', 'N'): False})

    @classmethod
    def ask(cls, question: str, options: dict) -> bool:

        titles = list()
        answers = dict()
        for option, value in options.items():
            if isinstance(option, str):
                titles.append(option)
                answers[option] = value
            else:
                titles.append(option[0])
                for answer in option:
                    answers[answer] = value

        question = f'{question}? [{"/".join(titles)}]: '
        query = f"{cls.CMD}{question}{cls.RESET}"
        res = input(query).strip()

        while res not in answers:
            res = input(query).strip()
        return answers[res]

    @classmethod
    def abort(cls, code: int = 1) -> None:
        raise SystemExit(code)

    @classmethod
    def echo(cls, msg: str) -> None:
        print(msg)  # noqa: T001

    @classmethod
    def log(cls, msg: str) -> None:
        if cls._verbosity >= 1:
            cls.echo(cls.LOG + msg + cls.RESET)
