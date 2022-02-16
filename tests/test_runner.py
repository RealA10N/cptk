from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from cptk.core.chef import Runner
from cptk.core.chef import RunnerResult

if TYPE_CHECKING:
    from utils import EasyDirectory


@dataclass
class Case:
    code: str
    output: str = None
    input: str = None
    error: str = None


class TestRunner:

    @staticmethod
    def _compare_results(case: Case, result: RunnerResult) -> None:
        if case.output is not None:
            assert result.outs == case.output

        if case.error is not None:
            assert result.errs == case.error

    @pytest.mark.parametrize(
        'case', (
            Case('print("Hello")', output='Hello\n'),
            Case('print("Hello", end="")', output='Hello'),
            Case(
                'print(f"Hello {input()}")',
                input='cptk\n', output='Hello cptk\n',
            ),
            Case(
                'print(f"Hello {input(\'Enter your name: \')}")',
                input='cptk\n', output='Enter your name: Hello cptk\n',
            ),
        ),
    )
    def test_running_python_script(
        self,
        case: Case,
        tempdir: EasyDirectory,
    ) -> None:

        run = Runner()
        filepath = tempdir.create(case.code, 'file.py')
        result = run.exec(f'{sys.executable} {filepath}', input=case.input)

        assert result.code == 0
        assert not result.timed_out
        self._compare_results(case, result)

    @pytest.mark.parametrize(
        'case', (
            Case(
                'from time import sleep\nsleep(10)\n',
                input='', output='', error='',
            ),
            Case(
                'from time import sleep\n'
                'print("I\'m tired...", flush=True)\n'
                'sleep(10)\n',
                input='', output="I'm tired...\n", error='',
            ),
            Case(
                'from time import sleep\nprint(input(), flush=True)\nsleep(10)\n',
                input='hello\n', output="hello\n", error='',
            ),
        ),
    )
    def test_running_python_timeout(
        self,
        case: Case,
        tempdir: EasyDirectory,
    ) -> None:
        run = Runner()
        filepath = tempdir.create(case.code, 'file.py')
        result = run.exec(
            f'{sys.executable} {filepath}',
            input=case.input, timeout=0.5,
        )

        assert result.code != 0
        assert result.timed_out
        self._compare_results(case, result)
