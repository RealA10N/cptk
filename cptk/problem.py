from dataclasses import dataclass, field

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Type, Any
    from cptk import Website


class Element:
    pass


@dataclass
class Problem(Element):
    website: 'Type[Website]' = field(compare=True)

    # required metadata
    uid: 'Any' = field(compare=True)
    name: str = field(compare=False)
    tests: 'List[Test]' = field(compare=False)

    # additional metadata
    contest: 'Contest' = field(default=None, compare=False)
    level: str = field(default=None, compare=False)
    section: str = field(default=None, compare=False)
    time_limit: float = field(default=None, compare=False)     # in Seconds
    memory_limit: float = field(default=None, compare=False)   # in MB


@dataclass
class Test(Element):
    input: str
    expected: str


@dataclass
class Contest(Element):
    website: 'Type[Website]' = field(compare=True)
    uid: 'Any' = field(compare=True)
    name: str = field(compare=False)
