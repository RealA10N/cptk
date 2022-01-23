from unittest import mock

import pytest
from freezegun import freeze_time

from .utils import Dummy
from cptk.core import Preprocessor
from cptk.exceptions import PreprocessError


@mock.patch('os.getlogin', lambda: 'User')
@freeze_time('2022-01-01')
class TestPreprocessor:

    @pytest.mark.parametrize('template, expected', (
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
