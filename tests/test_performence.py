from time import perf_counter

import pytest

from .utils import run


class TestPerformance:

    @pytest.mark.xfail
    def test_startup_time(self) -> None:
        start = perf_counter()
        run('cptk --help')
        t = perf_counter() - start

        assert t <= 0.1
