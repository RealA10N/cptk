import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from cptk.core.chef import Runner
if TYPE_CHECKING:
    from utils import EasyDirectory


@dataclass
class Case:
    code: str
    output: str = None
    input: str = None
    error: str = None


class TestRunner:

    @pytest.mark.parametrize('case', (
        Case('print("Hello")', output='Hello\n'),
        Case('print("Hello", end="")', output='Hello'),
        Case('print(f"Hello {input()}")',
             input='cptk\n', output='Hello cptk\n'),
        Case('print(f"Hello {input(\'Enter your name: \')}")',
             input='cptk\n', output='Enter your name: Hello cptk\n'),
    ))
    def test_running_python_script(
        self,
        case: Case,
        tempdir: 'EasyDirectory',
    ) -> None:

        run = Runner()
        filepath = tempdir.create(case.code, 'file.py')
        result = run.exec(f'{sys.executable} {filepath}', input=case.input)

        assert result.code == 0
        assert not result.timed_out

        if case.output is not None:
            assert result.outs == case.output

        if case.error is not None:
            assert result.errs == case.error
