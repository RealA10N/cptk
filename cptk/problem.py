from dataclasses import dataclass

from typing import Optional, List, TYPE_CHECKING, Type
if TYPE_CHECKING:
    from cptk import Website


@dataclass(frozen=True)
class Problem:
    website: Type['Website']

    # required metadata
    uid: int
    name: str
    tests: List['Test']

    # additional metadata
    level: str = None
    time_limit: float = None     # in Seconds
    memory_limit: float = None   # in MB


@dataclass(frozen=True)
class Test:
    input: str
    expected: str


@dataclass(frozen=True)
class Contest:
    website: Type['Website']
    uid: int
    name: str
