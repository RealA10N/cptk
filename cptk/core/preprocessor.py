import os
from datetime import datetime
from typing import TYPE_CHECKING

import jinja2
from slugify import slugify
if TYPE_CHECKING:
    from cptk.scrape import Problem


class Preprocessor:

    def __init__(self, problem: 'Problem') -> None:
        self._env = jinja2.Environment()
        self._env.globals['problem'] = problem
        self._env.filters['slug'] = slugify
        self._env.globals['user'] = os.getlogin()
        self._env.globals['now'] = datetime.now()

    def parse_string(self, string: str) -> str:
        try:
            return self._env.from_string(string).render()
        except Exception:
            # TODO: add warning
            return str()

    def parse_file_contents(self, path: str) -> None:
        with open(path, 'r', encoding='utf8') as file:
            data = file.read()

        new = self.parse_string(data)
        with open(path, 'w', encoding='utf8') as file:
            file.write(new)

    def parse_directory(self, path: str) -> None:
        for item in os.listdir(path):
            old = os.path.join(path, item)
            new = os.path.join(path, self.parse_string(item))
            os.rename(src=old, dst=new)

            if os.path.isdir(new):
                self.parse_directory(new)

            elif os.path.isfile(new):
                self.parse_file_contents(new)
