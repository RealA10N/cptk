from time import perf_counter

from .utils import run


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

    def test_startup_time(self) -> None:
        with time_limit(0.3):
            run('cptk --help')
