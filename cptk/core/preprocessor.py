import re
import os

from cptk.constants import PREPROCESSOR_PATTERN, PREPROCESSOR_INVALID

# pylint: disable=redefined-builtin


class Preprocessor:

    @classmethod
    def _replace_match(cls, match: 're.Match', globals: dict) -> str:
        code = match.group(1).strip()
        try:
            return eval(code, globals)
        except Exception:
            return PREPROCESSOR_INVALID

    @classmethod
    def parse_string(cls, string: str, globals: dict) -> str:
        return re.sub(
            PREPROCESSOR_PATTERN,
            string=string,
            repl=lambda m: cls._replace_match(m, globals),
        )

    @classmethod
    def parse_file_contents(cls, path: str, globals: dict) -> None:
        with open(path, 'r', encoding='utf8') as file:
            data = file.read()
        new = cls.parse_string(data, globals)
        if data != new:
            with open(path, 'w', encoding='utf8') as file:
                file.write(data)

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
