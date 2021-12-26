from dataclasses import dataclass, field

from typing import Optional, List, TYPE_CHECKING, Type
if TYPE_CHECKING:
    from cptk import Website


@dataclass(frozen=True)
class Problem:
    website: Type['Website'] = field(compare=True)

    # required metadata
    uid: int = field(compare=True)
    name: str = field(compare=False)
    tests: List['Test'] = field(compare=False)

    # additional metadata
    level: str = field(default=None, compare=False)
    time_limit: float = field(default=None, compare=False)     # in Seconds
    memory_limit: float = field(default=None, compare=False)   # in MB


@dataclass(frozen=True)
class Test:
    input: str
    expected: str


@dataclass(frozen=True)
class Contest:
    website: Type['Website'] = field(compare=True)
    uid: int = field(compare=True)
    name: str = field(compare=False)
