import os
import re
from argparse import ArgumentTypeError
from functools import lru_cache
from typing import Callable
from typing import TypeVar
T = TypeVar('T')


class cptkException(Exception):
    """ Base cptk exception. All exceptions raised and created by cptk should
    inherent from this one. Note that this expection can't be defined in
    'exceptions.py' to avoid circular import errors. (: """


def cached_property(f: Callable[..., T]) -> T:
    """ The builtin cached_property decorator was introduced in py3.8.
    This is a simple implementation of the decortor that can be ran with older
    Python versions. https://tinyurl.com/smhlght """

    return property(lru_cache(None)(f))


@lru_cache
def _url_regex() -> str:
    # Cached so the regex is compiled only once,
    # and only if needed at all.
    return re.compile(
        r"(\w+://)?"                # protocol (optional)
        r"(\w+\.)?"                 # host (optional)
        r"((\w+)\.(\w+))"           # domain
        r"(\.\w+)*"                 # top-level domain (optional, can have > 1)
        r"([\w\-\._\~/]*)*(?<!\.)"  # path, params, anchors, etc. (optional)
    )


def valid_url(url) -> bool:
    return bool(_url_regex().fullmatch(url))


def path_validator(
    dir_ok=True,
    file_ok=True,
    must_exist=False,
) -> Callable[[str], str]:
    def validator(path: str) -> str:
        path = os.path.normpath(path)

        if not file_ok and os.path.isfile(path):
            raise ArgumentTypeError(f"{path!r} is a file")

        if not dir_ok and os.path.isdir(path):
            raise ArgumentTypeError(f"{path!r} is a direcotry")

        if must_exist and not os.path.exists(path):
            raise ArgumentTypeError(f"path {path!r} doesn't exist")

        return path
    return validator


def url_validator(url: str) -> str:
    if not valid_url(url):
        raise ArgumentTypeError(f'invalid url {url!r}')
    return url
