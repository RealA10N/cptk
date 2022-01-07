import os
import pytest

from cptk.core import Configuration
from cptk.exceptions import (
    ConfigFileNotFound,
    ConfigFileValueError,
    ConfigFileParsingError,
)

from typing import Optional


class Pet(Configuration):
    name: str
    age: int
    type: Optional[str]


class TestConfiguration:
    """ Tests the 'load' classmethod of all Configuration models. """

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

        data = Pet.load(path)
        assert isinstance(data, Pet)
        assert data.dict() == expected

    def test_file_not_found(self, tempdir) -> None:
        path = tempdir.join('config.yaml')
        assert not os.path.exists(path)

        with pytest.raises(ConfigFileNotFound) as err:
            Pet.load(path)

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
            Pet.load(path)

    @pytest.mark.parametrize('yaml', (
        """
        name: doggo
        type: -: -:
        """,
    ))
    def test_yaml_parse_error(self, tempdir, yaml) -> None:
        path = tempdir.create('broken.yaml', yaml)

        with pytest.raises(ConfigFileParsingError):
            Pet.load(path)

    @pytest.mark.parametrize('pet', (
        Pet(name='Boogo', age=123, type='Dog'),
        Pet(name='Lora', age=1),
    ))
    def test_dump(self, tempdir, pet: Pet) -> None:
        path = tempdir.join('pet.yaml')

        assert not os.path.isfile(path)
        pet.dump(path)
        assert os.path.isfile(path)

        newpet = Pet.load(path)
        assert pet == newpet
