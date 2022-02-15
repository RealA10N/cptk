import os
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from yaml import dump
from yaml import safe_load
from yaml import YAMLError

from cptk.utils import cptkException
if TYPE_CHECKING:
    from typing import Type, TypeVar, Tuple

    T = TypeVar('T')


class ConfigFileError(cptkException):
    """ Base cptkException for all errors thrown from the 'load_config_file'
    function, while trying to load a YAML configuration file. """


class ConfigFileNotFound(ConfigFileError, FileNotFoundError):
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Can't find configuration file {path!r}")


class ConfigFileValueError(ConfigFileError, ValueError):

    def __init__(self, path: str, errors: dict) -> None:
        self.path = path
        self.errors = errors
        super().__init__(self.__generate_error_message())

    def __generate_error_message(self) -> str:
        er = 'error' if len(self.errors) == 1 else f'{len(self.errors)} errors'
        s = f"{er} found in {self.path!r}:"

        for error in self.errors:
            path = '.'.join(error['loc']) if error['loc'] else '.'
            s += f"\nUnder {path!r}: {error['msg']}"

        return s


class ConfigFileParsingError(ConfigFileError):
    def __init__(self,
                 path: str,
                 error: str,
                 position: 'Tuple[int, int]' = None,
                 ) -> None:
        self.path = path
        self.error = error
        self.position = position
        super().__init__(self.__generate_error_message())

    def __generate_error_message(self) -> str:
        s = f"Error while parsing {self.path!r}\n"
        s += f"Under line {self.position[0]}: {self.error}"
        return s


class Configuration(BaseModel):

    @classmethod
    def load(cls: 'Type[T]', path: str) -> 'T':
        """ Load information from a YAML configuration file and dump it into a
        pydantic model. Raises relevent expections if the given file path isn't
        found, the YAML file can't be parsed, or the data doesn't match the
        pydantic model. """

        try:
            with open(path, 'r', encoding='utf8') as file:
                data = safe_load(file)

        except FileNotFoundError:
            raise ConfigFileNotFound(path)

        except YAMLError as err:
            mark = err.problem_mark
            pos = (mark.line + 1, mark.column + 1)
            raise ConfigFileParsingError(path, err.problem, pos)

        if not isinstance(data, dict):
            raise ConfigFileValueError(
                path, [{'loc': (), 'msg': "file isn't in dictionary format"}])

        try:
            return cls(**data)
        except ValidationError as e:
            raise ConfigFileValueError(path, e.errors()) from e

    def yaml(self) -> str:
        """ Converts the object into a YAML string. """

        return dump(self.dict(exclude_unset=True), sort_keys=False)

    def dump(self, path: str) -> None:
        """ Dumps the pydantic model into the given file in YAML format. """

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf8') as file:
            file.write(self.yaml())
