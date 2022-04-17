from __future__ import annotations

import os
import sys
from typing import Callable
from typing import TYPE_CHECKING

import blessings

from cptk.utils import cptkException

if TYPE_CHECKING:  # pragma: no cover
    from subprocess import CompletedProcess


class SystemRunError(cptkException):
    """ Raised by System.run if something goes wrong. """


class System:

    terminal = blessings.Terminal()
    _verbosity = 0
    _yes_stack = 0

    @classmethod
    def run(
        cls,
        cmd: str,
        errormsg: str = None,
        verbose: bool = None,
    ) -> CompletedProcess:
        """ Runs the given command in the terminal. If 'errormsg' is provided,
        asserts that the returncode from the process is zero, and if not,
        raises an SystemRunError with the given message. If 'verbose' is
        provided, it overwrites the classes verbosity setting. """

        import subprocess

        if verbose is None:
            verbose = cls._verbosity >= 2

        if verbose:
            cls.echo(cls.terminal.bright_black(cmd))

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
    def success(cls, msg: str, title: str = 'SUCCESS', *args, **kwargs) -> None:
        title = cls.terminal.bold_white_on_green(f' {title.upper()} ')
        cls.echo(f'{title} {msg}', *args, **kwargs)

    @classmethod
    def error(
            cls,
            error: str | Exception,
            title: str = 'ERROR',
            *args, **kwargs,
    ) -> None:
        if isinstance(error, Exception):
            error = cls._expection_to_msg(error)

        title = cls.terminal.bold_white_on_red(f' {title.upper()} ')
        cls.echo(f"{title} {error}", *args, **kwargs)

    @classmethod
    def unexpected_error(cls, error: Exception) -> None:

        title = type(error).__name__
        desc = cls._expection_to_msg(error)
        msg = title if not desc else f'{title}: {desc}'

        cls.error(msg, title='UNEXPECTED ERROR')

        import traceback
        import platform
        import cptk
        # import cptt

        cls.details(
            ''.join(
                traceback.format_exception(
                    type(error), error, error.__traceback__,
                ),
            ),
        )

        cls.log(
            f'Python {platform.python_version()}, '
            f'cptk {cptk.__version__}',
            # f'cptt {cptt.__version__}',
            # TODO: uncomment when cptt is used by cptk!
        )

        if not cls._verbosity:
            cls.title('Use -v or -vv to get more details')

    @classmethod
    def abnormal_exit(cls) -> None:
        cls.echo(cls.terminal.bold_white_on_red(' ABNORMAL EXIT '))

    @classmethod
    def warn(cls, msg: str, *args, **kwargs) -> None:
        cls.echo(
            cls.terminal.bold_black_on_yellow(
                ' WARNING ',
            ) + ' ' + msg, *args, **kwargs,
        )

    @classmethod
    def confirm(cls, question: str) -> bool:
        if cls.pop_yes():
            return True
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
        query = cls.terminal.yellow(question)
        res = input(query).strip()

        while res not in answers:
            res = input(query).strip()
        return answers[res]

    @classmethod
    def abort(cls, code: int = 1) -> None:
        raise SystemExit(code)

    @classmethod
    def echo(cls, msg: str, *args, **kwargs) -> None:
        print(msg, *args, **kwargs)  # noqa: T001

    @classmethod
    def title(cls, msg: str, *args, **kwargs) -> None:
        cls.echo(cls.terminal.bold(msg), *args, **kwargs)

    @classmethod
    def log(cls, msg: str, *args, **kwargs) -> None:
        if cls._verbosity >= 1:
            cls.echo(cls.terminal.bold_bright_black(msg), *args, **kwargs)

    @classmethod
    def details(cls, msg: str, *args, **kwargs) -> None:
        if cls._verbosity >= 2:
            cls.echo(cls.terminal.bright_black(msg), *args, **kwargs)

    @classmethod
    def two_sided(
            cls,
            left: tuple[Callable[[], None], int],
            right: tuple[Callable[[], None], int],
            pad: str = ' ', width=None,
    ) -> None:
        """ Recives two printing functions and the sizes of the strings that they
        will print, and calls them in such a way that will print them in the same
        line padded to different sides of the terminal window. """

        width = width or os.get_terminal_size().columns

        leftf, lenleft = left
        rightf, lenright = right

        leftf()

        if lenleft + lenright > width:
            right_pad = max(width - lenright, 0)
            cls.echo('\n' + right_pad * pad, end='')
        else:
            mid_pad = width - lenleft - lenright
            cls.echo(mid_pad * pad, end='')

        rightf()
