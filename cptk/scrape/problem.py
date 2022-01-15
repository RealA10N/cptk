from dataclasses import dataclass, field

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Type, Any
    from cptk.scrape import Website


class Element:
    pass


@dataclass
class Problem(Element):
    website: 'Type[Website]' = field(compare=True)

    # required metadata
    uid: 'Any' = field(compare=True, hash=True)
    name: str = field(compare=False)
    url: str = field(compare=False)

    contest: 'Contest' = field(default=None, compare=False)

    tests: 'List[Test]' = field(default_factory=list, compare=False)
    time_limit: float = field(default=None, compare=False)     # in Seconds
    memory_limit: float = field(default=None, compare=False)   # in MB


@dataclass(unsafe_hash=True)
class Test(Element):
    input: str
    expected: str = None


@dataclass(unsafe_hash=True)
class Contest(Element):
    website: 'Type[Website]' = field(compare=True)
    uid: 'Any' = field(compare=True)
    name: str = field(compare=False)
