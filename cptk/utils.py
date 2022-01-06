from functools import lru_cache

from typing import Callable, TypeVar
T = TypeVar('T')


def cached_property(f: Callable[..., T]) -> T:
    """ The builtin cached_property decorator was introduced in py3.8.
    This is a simple implementation of the decortor that can be ran with older
    Python versions. https://tinyurl.com/smhlght """

    return property(lru_cache(f))
