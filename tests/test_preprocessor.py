import pytest

from .utils import Dummy
from cptk.core import Preprocessor


class TestPreprocessor:

    @pytest.mark.parametrize('template, expected', (
        ('{{invalid}}', ''),
        ('{{invalid|slug}}', ''),
        ('{{invalid|invalid}}', ''),
        ('{{problem.name}}', 'name'),
    ))
    def test_invalid_input(
        self,
        template: str,
        expected: str,
        dummy: 'Dummy',
    ):
        prob = dummy.get_dummy_problem()
        prob.name = 'name'

        pre = Preprocessor(prob)
        assert pre.parse_string(template) == expected
