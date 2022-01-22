from time import perf_counter
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy

from .utils import run
from cptk.local import LocalProject


class time_limit:
    def __init__(self, limit: float) -> None:
        self.limit = limit

    def __enter__(self):
        self.start = perf_counter()

    def __exit__(self, *_, **__):
        diff = perf_counter() - self.start
        if diff > self.limit:
            raise TimeoutError(
                f'Waited for {diff:03}, '
                f'limit is {self.limit:0.3}'
            )


class TestPerformance:

    @pytest.mark.xfail
    def test_startup_time(self) -> None:
        with time_limit(0.05):
            run('cptk --help')

    def test_lots_of_moves(
        self,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ) -> None:
        with time_limit(0.5):
            proj = LocalProject.init(tempdir.path)
            proj.config.clone.path = 'clone0/${{problem.name}}'

            prob_a = dummy.get_dummy_problem()
            prob_a.name = 'A'

            proj.clone_problem(prob_a)

            prob_b = dummy.get_dummy_problem()
            prob_b.name = 'B'

            for i in range(1000):
                proj.move(f'clone{i}', f'clone{i+1}')

            proj.clone_problem(prob_b)
