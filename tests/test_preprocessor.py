import os
import pytest

from cptk.core import Preprocessor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .utils import EasyDirectory


class TestPreprocessor:

    @pytest.mark.parametrize('inp, out, data', (
        ('${{hello}}', 'hi', {'hello': 'hi'}),
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
