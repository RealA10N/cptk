import os
import re
from copy import copy
from typing import Match
from typing import Tuple

from cptk.constants import PREPROCESSOR_INVALID
from cptk.constants import PREPROCESSOR_PATTERN

# for readability, we redefine the global 'globals' variable
# pylint: disable=redefined-builtin

HERE = os.path.dirname(__file__)
DEFAULTS = os.path.join(HERE, '..', 'defaults')
DEFAULT_PREPROCESS = os.path.join(DEFAULTS, 'preprocess', 'preprocess.py')


class Preprocessor:

    @classmethod
    def _replace_match(cls, match: Match, globals: dict) -> str:
        code = match.group(1).strip()
        try:
            return eval(code, globals)  # pylint: disable=eval-used
        except Exception:  # pylint: disable=broad-except
            return PREPROCESSOR_INVALID

    @classmethod
    def _parse_count_string(
        cls,
        string: str,
        globals: dict,
    ) -> Tuple[str, int]:
        """ Parses the string and in addition returns the number of replacements
        it has preformed. """
        return re.subn(
            PREPROCESSOR_PATTERN,
            string=string,
            repl=lambda m: cls._replace_match(m, globals),
        )

    @classmethod
    def parse_string(cls, string: str, globals: dict) -> str:
        return cls._parse_count_string(string, globals)[0]

    @classmethod
    def parse_file_contents(cls, path: str, globals: dict) -> None:
        with open(path, 'r', encoding='utf8') as file:
            data = file.read()

        new, count = cls._parse_count_string(data, globals)

        if count > 0:
            with open(path, 'w', encoding='utf8') as file:
                file.write(new)

    @classmethod
    def parse_directory(cls, path: str, globals: dict) -> None:
        for item in os.listdir(path):
            old = os.path.join(path, item)
            new = os.path.join(path, cls.parse_string(item, globals))
            os.rename(src=old, dst=new)

            if os.path.isdir(new):
                cls.parse_directory(new, globals)

            elif os.path.isfile(new):
                cls.parse_file_contents(new, globals)

    @classmethod
    def load_file(cls, path: str, globals: dict = None) -> dict:
        """ Recives a path to a Python file, excutes it and returns its globals.
        If globals are given, the file is executed with the given globals
        pre-defined. If the given file contains a '__all__' list, only objects
        from the list will be returned. """

        if globals is None:
            globals = dict()

        globals = copy(globals)

        with open(path, 'r', encoding='utf8') as file:
            code = file.read()

        try:
            exec(code, globals)  # pylint: disable=exec-used
        except Exception:  # pylint: disable=broad-except
            pass  # TODO: print a warning

        if '__all__' in globals:
            return {
                name: g
                for name, g in globals.items()
                if name in globals['__all__']
            }

        return globals
