import os
import platform
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

import jinja2
from slugify import slugify

if TYPE_CHECKING:
    from cptk.scrape import Problem
    from typing import Type, TypeVar
    T = TypeVar('T')

from cptk.utils import cptkException


class PreprocessError(cptkException, ABC):

    def __init__(self, error: Exception) -> None:
        self.jinja_error = error
        super().__init__(self._generate_error_message())

    @abstractmethod
    def _generate_error_message(self,) -> str:
        pass


class PreprocessStringError(PreprocessError):
    def _generate_error_message(self) -> str:
        return ', '.join(self.jinja_error.args)


class PreprocessFileError(PreprocessError):
    def __init__(self, error: Exception, path: str) -> None:
        self.path = path
        super().__init__(error)

    def _generate_error_message(self) -> str:
        return f'In {self.path}: ' + ', '.join(self.jinja_error.args)

    @classmethod
    def from_string_err(
        cls: 'Type[T]',
        path: str,
        err: PreprocessStringError,
    ) -> 'T':
        return cls(err.jinja_error, path)


class PreprocessNameError(PreprocessError):
    def __init__(self, error: Exception, name: str) -> None:
        self.name = name
        super().__init__(error)

    def _generate_error_message(self) -> str:
        return f'In {self.name}: ' + ', '.join(self.jinja_error.args)

    @classmethod
    def from_string_err(
        cls: 'Type[T]',
        name: str,
        err: PreprocessStringError,
    ) -> 'T':
        return cls(err.jinja_error, name)


class Preprocessor:

    def __init__(self, problem: 'Problem') -> None:
        self._env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        self._env.globals.update({
            key: val
            for key, val in {
                'problem': problem,
                'now': datetime.now(),
                'slug': slugify,
                'system': platform.system(),
                'user': self.__try(os.getlogin),
            }.items() if val is not None
        })

        # Slug is a global to allow the "slug(...)" syntax,
        # and a filter to allow the "... | slug" syntax.
        self._env.filters.update({'slug': slugify, })

        # Cptk considers None values as undefined.
        # This means that scopes like {% if v is defined %} where v is None
        # won't be executed.

        def defined(v):
            return not isinstance(v, jinja2.Undefined) and v is not None

        def undefined(v):
            return isinstance(v, jinja2.Undefined) or v is None

        self._env.tests.update({'defined': defined, 'undefined': undefined})

    @staticmethod
    def __try(fun, default=None):
        try:
            return fun()
        except Exception:
            return default

    def parse_string(self, string: str) -> str:
        try:
            return self._env.from_string(string).render()
        except Exception as err:
            raise PreprocessStringError(err)

    def parse_file_contents(self, path: str) -> None:
        with open(path, 'r', encoding='utf8') as file:
            data = file.read()

        try:
            new = self.parse_string(data)
        except PreprocessStringError as err:
            raise PreprocessFileError.from_string_err(path, err)

        with open(path, 'w', encoding='utf8') as file:
            file.write(new)

    def parse_directory(self, path: str) -> None:
        for item in os.listdir(path):
            old = os.path.join(path, item)

            try:
                new = os.path.join(path, self.parse_string(item))
            except PreprocessStringError as err:
                raise PreprocessNameError.from_string_err(old, err)

            os.rename(src=old, dst=new)

            if os.path.isdir(new):
                self.parse_directory(new)

            elif os.path.isfile(new):
                self.parse_file_contents(new)
