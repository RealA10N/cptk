import os
from copy import copy
from dataclasses import is_dataclass
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from cptk.core import Preprocessor
if TYPE_CHECKING:
    from .utils import EasyDirectory


class TestPreprocessor:

    @pytest.mark.parametrize('inp, out, data', (
        ('${{hello}}', 'hi', {'hello': 'hi'}),
        ('${{ str(eval("3+2")) }}', '5', {}),
        ('${{hello}} ${{who}}', 'hi alon', {'hello': 'hi', 'who': 'alon'}),
        ('${{hello}} ${{missing}}', 'hi ?', {'hello': 'hi', 'who': 'alon'}),
        ('hello ${{ name }}!', 'hello Alon!', {'name': 'Alon'}),
        ('hello ${{ name.upper() }}!', 'hello ALON!', {'name': 'Alon'}),
        ('hello ${{ missing }}', 'hello ?', {}),
    ))
    def test_strings(self, inp: str, out: str, data: dict) -> None:
        res = Preprocessor.parse_string(inp, data)
        assert res == out

    @pytest.mark.parametrize('inp, out, data', (
        ('Hello ${{ who }}!', 'Hello There!', {'who': 'There'}),
    ))
    def test_file(self,
                  tempdir: 'EasyDirectory',
                  inp: str,
                  out: str,
                  data: dict,
                  ) -> None:

        path = tempdir.create(inp, 'file.txt')
        Preprocessor.parse_file_contents(path, data)

        print(path)

        with open(path, 'r', encoding='utf8') as file:
            res = file.read()

        assert res == out

    def test_file_no_changes(self, tempdir: 'EasyDirectory') -> None:
        path = tempdir.create("no preprocessing here!", 'data.txt')
        before = os.path.getmtime(path)
        data = {'hello': 'there'}

        Preprocessor.parse_file_contents(path, data)
        Preprocessor.parse_directory(tempdir.path, data)

        # Assert that the file hasn't been modified
        assert os.path.getmtime(path) == before

    def test_directory(self, tempdir: 'EasyDirectory') -> None:

        # Create two files and two directories
        tempdir.create('hello from ${{project}}!', '${{filename}}.txt')
        dir1 = tempdir.join('dir-${{dirname}}')
        os.makedirs(dir1)
        file2 = tempdir.create('hello!', dir1, '${{filename}}.${{ext}}')
        dir2 = tempdir.join('${{dirname}}', 'another-${{ something }}')
        os.makedirs(dir2)

        data = {
            'project': 'cptk',
            'filename': 'info',
            'dirname': 'dir',
            'ext': 'info',
            'something': 'dir',
        }

        Preprocessor.parse_directory(tempdir.path, data)

        # Test first file
        file1 = tempdir.join('info.txt')
        assert os.path.isfile(file1)
        with open(file1, 'r', encoding='utf8') as file:
            assert file.read() == 'hello from cptk!'

        # Test first directory
        dir1 = tempdir.join('dir-dir')
        assert os.path.isdir(dir1)

        # Test second file
        file2 = os.path.join(dir1, 'info.info')
        assert os.path.isfile(file2)
        with open(file2, 'r', encoding='utf8') as file:
            assert file.read() == 'hello!'

        # Test second (nested) directory
        dir2 = tempdir.join('dir', 'another-dir')
        assert os.path.isdir(dir2)

    @pytest.mark.parametrize('source, expected', (
        (
            """
                name = "Alon"
                project = "cptk"
                number = 123
            """,
            {
                'name': 'Alon',
                'project': 'cptk',
                'number': 123,
            },
        ),
        (
            """
                import random
                name = "cptk"
                date = (10, 1, 2022)
                __all__ = ['date']
            """,
            {
                'date': (10, 1, 2022),
            }
        )
    ))
    def test_load_file(self, tempdir: 'EasyDirectory', source: str, expected: dict) -> None:
        path = tempdir.create(dedent(source), 'script.py')

        data = {
            key: value
            for key, value in Preprocessor.load_file(path).items()
            if not key.startswith('_')
        }

        assert data == expected

    def test_load_file_new_objects(self, tempdir: 'EasyDirectory') -> None:

        source = """
            from dataclasses import dataclass
            from typing import Optional

            @dataclass
            class Person:
                name: str
                age: Optional[int] = None

            class Hello:

                def __init__(self, person: Person) -> None:
                    self.person = person

                def greet(self):
                    return f'Hello {self.person.name}!'

            __all__ = ['Person', 'Hello']
        """

        path = tempdir.create(dedent(source), 'script.py')
        data = Preprocessor.load_file(path)
        Hello = data.get('Hello')
        Person = data.get('Person')

        assert Person is not None
        assert isinstance(Hello, type)
        assert is_dataclass(Person)

        yuval, talbi = Person('Yuval'), Person('Ido Talbi', age=17)
        assert yuval.name == 'Yuval'
        assert yuval.age is None
        assert talbi.name == 'Ido Talbi'
        assert talbi.age == 17

        assert Hello is not None
        assert isinstance(Hello, type)
        assert Hello(yuval).greet() == 'Hello Yuval!'
        assert Hello(talbi).greet() == 'Hello Ido Talbi!'

    def test_fail_load_file(self, tempdir: 'EasyDirectory'):
        src = 'syntax error, this is not a valid python script!'
        path = tempdir.create(src, 'script.py')

        glbs = {'x': 5, 'y': None}

        data = {
            key: value
            for key, value in Preprocessor.load_file(path, copy(glbs)).items()
            if not key.startswith('_')
        }

        assert data == glbs
