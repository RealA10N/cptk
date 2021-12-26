from dataclasses import dataclass, field

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Type
    from cptk import Website


@dataclass(frozen=True)
class Problem:
    website: 'Type[Website]' = field(compare=True)

    # required metadata
    uid: int = field(compare=True)
    name: str = field(compare=False)
    tests: 'List[Test]' = field(compare=False)

    # additional metadata
    contest: 'Contest' = field(default=None, compare=False)
    level: str = field(default=None, compare=False)
    time_limit: float = field(default=None, compare=False)     # in Seconds
    memory_limit: float = field(default=None, compare=False)   # in MB


@dataclass(frozen=True)
class Test:
    input: str
    expected: str


@dataclass(frozen=True)
class Contest:
    website: 'Type[Website]' = field(compare=True)
    uid: int = field(compare=True)
    name: str = field(compare=False)
