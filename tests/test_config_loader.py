import os
import pytest

from cptk.core import load_config_file

from pydantic import BaseModel
from typing import Literal, Union


from cptk.exceptions import ConfigFileNotFound


class Pet(BaseModel):
    name: str
    age: int
    type: Union[Literal['Dog'], Literal['Cat']]


class TestConfigLoader:
    """ Tests the 'load_config_file' function location in
    'cptk.core.config'. """

    @pytest.mark.parametrize('case', (
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
            age: 8
            type: Cat
            """,
            {'name': 'Milky', 'age': 8, 'type': 'Cat'},
        ),
    ))
    def test_valids(self, case, tempdir) -> None:
        yaml, expected = case
        path = tempdir.create('pet.yaml', yaml)

        data = load_config_file(path, Pet)
        assert isinstance(data, Pet)
        assert data.dict() == expected

    def test_file_not_found(self, tempdir) -> None:
        path = tempdir.join('config.yaml')
        assert not os.path.exists(path)

        with pytest.raises(ConfigFileNotFound):
            load_config_file(path, Pet)
