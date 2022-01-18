from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cptk.scrape import Problem
    from bs4 import BeautifulSoup
    from typing import Union, Optional, List


@dataclass(frozen=True)
class PageInfo:
    """ A simple dataclass that contains all information about a webpage that
    is required by the 'Website' classes to preform their actions and queries.
    """

    url: str
    data: 'BeautifulSoup' = field(repr=False)


class Website(ABC):
    """ An abstract class that represents a website that is supported by cptk.
    Has different methods that can fetch data and information from the website.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """ The name of the website. """

    @property
    @abstractmethod
    def domain(self) -> 'Union[str, List[str]]':
        """ A single domain or a list of domains that are represented by this
        class. """

    @abstractmethod
    def is_problem(self, info: PageInfo) -> bool:
        """ Returns True only if the given page information describes a page
        with a single problem. """

    @abstractmethod
    def to_problem(self, info: PageInfo) -> 'Optional[Problem]':
        """ Constructs and a Problem instance that represents the problem that
        is displayed in the given page. If the given page doesn't display a
        single and unique problem, returns None. """
