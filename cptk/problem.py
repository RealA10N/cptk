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
    section: Optional[str]
    time_limit: Optional[float]     # in Seconds
    memory_limit: Optional[float]   # in MB


@dataclass(frozen=True)
class Test:
    problem: 'Problem'

    input: str
    expected: str


@dataclass(frozen=True)
class Contest:
    website: Type['Website']
    uid: int
    name: str
