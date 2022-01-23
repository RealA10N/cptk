import os
from typing import TYPE_CHECKING
from unittest import mock

from cptk.core.preprocessor import PreprocessFileError
from cptk.core.preprocessor import PreprocessNameError

if TYPE_CHECKING:
    from .utils import Dummy, EasyDirectory

import pytest
from freezegun import freeze_time

from cptk.core import Preprocessor
from cptk.exceptions import PreprocessError


@mock.patch('os.getlogin', lambda: 'User')
@freeze_time('2022-01-01')
class TestPreprocessor:

    @pytest.mark.parametrize('template, expected', (
        ('', ''),
        ('no template here', 'no template here'),
        ('{{ "Hello There!" | slug }}', 'hello-there'),
        ('x-{{ "hi~" | slug }}-y', 'x-hi-y'),
        ('{{ slug("Hello There!") }}', 'hello-there'),
        ('{{problem.name}}', 'Test Problem'),
        ('{{user}}', 'User'),
        ('{{now.ctime()}}', 'Sat Jan  1 00:00:00 2022'),
    ))
    def test_valid_strings(
        self,
        template: str,
        expected: str,
        dummy: 'Dummy',
    ):
        pre = Preprocessor(dummy.get_dummy_problem())
        assert pre.parse_string(template) == expected

    @pytest.mark.parametrize('string', (
        '{{invalid}}',
        '{{problem.name|invalid}}',
    ))
    def test_undefined_raises(self, string: str, dummy: 'Dummy'):
        pre = Preprocessor(dummy.get_dummy_problem())
        with pytest.raises(PreprocessError):
            pre.parse_string(string)

    @pytest.mark.parametrize('template, expected', (
        ('{{ user }} - {{ problem.name }}', 'User - Test Problem'),
        ('', ''),
    ))
    def test_valid_files(
        self,
        template: str,
        expected: str,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ):
        pre = Preprocessor(dummy.get_dummy_problem())
        path = tempdir.create(template, 'file.txt')
        pre.parse_file_contents(path)
        with open(path, 'r') as file:
            actual = file.read()
        assert actual == expected

    @pytest.mark.parametrize('template', (
        '{{ invald }}',
    ))
    def test_invalid_files(
        self,
        template: str,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ):
        pre = Preprocessor(dummy.get_dummy_problem())
        path = tempdir.create(template, 'file.txt')

        with pytest.raises(PreprocessFileError):
            pre.parse_file_contents(path)

        assert os.path.isfile(path)

        with open(path, 'r') as file:
            actual = file.read()

        assert actual == template

    @pytest.mark.parametrize('name', (
        '{{ invalid }}',
    ))
    def test_invalid_file_name(
        self,
        name: str,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ):
        pre = Preprocessor(dummy.get_dummy_problem())
        tempdir.create('', name)
        with pytest.raises(PreprocessNameError):
            pre.parse_directory(tempdir.path)
