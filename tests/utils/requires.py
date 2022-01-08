import pytest
from shutil import which


def requires(name: str):
    """ A decorator for pytest tests that skips the test if a program with the
    given name is not found of the machine. """

    def decorator(f):
        dec = pytest.mark.skipif(
            which(name) is None,
            reason=f"Requires program {name!r}",
        )
        return dec(f)

    return decorator
