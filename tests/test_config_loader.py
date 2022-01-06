import os
from pydantic.config import Extra
import pytest

from cptk.core import load_config_file

from pydantic import BaseModel
from typing import Optional


from cptk.exceptions import ConfigFileNotFound, ConfigFileValueError, ConfigFileParsingError


class Pet(BaseModel):
    name: str
    age: int
    type: Optional[str]


class TestConfigLoader:
    """ Tests the 'load_config_file' function location in
    'cptk.core.config'. """

    @pytest.mark.parametrize('yaml, expected', (
        (
            """
            name: Shocko
            age: 4
            type: Dog
            """,
            {'name': 'Shocko', 'age': 4, 'type': 'Dog'},
        ),
        (
            """
            name: Milky
            age: 8.17
            """,
            {'name': 'Milky', 'age': 8, 'type': None},
        ),
    ))
    def test_valids(self, yaml, expected, tempdir) -> None:
        path = tempdir.create('pet.yaml', yaml)

        data = load_config_file(path, Pet)
        assert isinstance(data, Pet)
        assert data.dict() == expected

    def test_file_not_found(self, tempdir) -> None:
        path = tempdir.join('config.yaml')
        assert not os.path.exists(path)

        with pytest.raises(ConfigFileNotFound) as err:
            load_config_file(path, Pet)

        assert err.value.path == path

    @pytest.mark.parametrize('yaml', (
        "",
        """
        name: Haribo
        type: Dog
        """,
        """
        name: null
        age: 123
        type: Cow
        """,
        """
        name: Mooooo
        age: NaN
        type: Cow
        """,
    ))
    def test_value_errors(self, tempdir, yaml) -> None:
        path = tempdir.create('pet.yaml', yaml)

        with pytest.raises(ConfigFileValueError) as err:
            load_config_file(path, Pet)

    @pytest.mark.parametrize('yaml', (
        """
        name: doggo
        type: -: -:
        """,
    ))
    def test_yaml_parse_error(self, tempdir, yaml) -> None:
        path = tempdir.create('broken.yaml', yaml)

        with pytest.raises(ConfigFileParsingError):
            load_config_file(path, Pet)
