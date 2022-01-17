from dataclasses import dataclass, field

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Any
    from cptk.scrape import Website
    from datetime import datetime


@dataclass(unsafe_hash=True)
class Scraped:
    """ Any information that is scraped using cptk is represented using
    instanaces of the 'Scraped' object, or instances of classes that inherent
    from it. """

    _uid: 'Any' = field(compare=True, hash=True)
    website: 'Website' = field(compare=True)
    name: str = field(compare=False)
    url: str = field(compare=False)


@dataclass(unsafe_hash=True)
class Problem(Scraped):
    """ A basic problem that is scraped using cptk. Most website implement their
    own 'Problem' class which inherits from this one and can store additional
    information. """

    group: 'ProblemGroup' = field(default=None, compare=False)
    tests: 'List[Test]' = field(default_factory=list, compare=False)
    time_limit: float = field(default=None, compare=False)     # in Seconds
    memory_limit: float = field(default=None, compare=False)   # in MB


@dataclass(unsafe_hash=True)
class ProblemGroup(Scraped):
    pass


@dataclass(unsafe_hash=True)
class Contest(ProblemGroup):
    active: bool = field(default=None, compare=False)
    start_time: 'datetime' = field(default=None, compare=False)
    end_time: 'datetime' = field(default=None, compare=False)


@dataclass(unsafe_hash=True)
class Test:
    input: str
    expected: str = None
