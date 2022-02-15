import os
import re
import shutil
from argparse import ArgumentTypeError
from functools import lru_cache
from typing import Callable
from typing import Generator
from typing import List
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


def find_tree_files(dir: str) -> Generator[str, None, None]:
    """ Yields all files in the directory as absolute paths. """

    if not os.path.isdir(dir): return

    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isdir(path): yield from find_tree_files(path)
        elif os.path.isfile(path): yield path


def find_common_files(a: str, b: str) -> List[str]:
    """ Returns a list of files that share the same relative path in both
    directories a and b. """

    # To preserve the order of the files, we use the order of a_files
    a_files = list(os.path.relpath(p, start=a) for p in find_tree_files(a))
    b_files = (os.path.relpath(p, start=b) for p in find_tree_files(b))
    commons = set(a_files).intersection(b_files)
    return [p for p in a_files if p in commons]


def soft_tree_copy(src: str, dst: str) -> None:
    """ Copies all files from the source directory into the destination
    directory, recursively. If the file already exists in the destination
    directory, it will be overwritten. If some subdirectory src/a exists, it
    will be created in the destintation directory, even if there are no files
    inside it in the source directory. """

    os.makedirs(dst, exist_ok=True)

    for name in os.listdir(src):
        item_src = os.path.join(src, name)
        item_dst = os.path.join(dst, name)

        if os.path.isdir(item_src): soft_tree_copy(item_src, item_dst)
        elif os.path.isfile(item_src): shutil.copyfile(item_src, item_dst)


@lru_cache(None)
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
