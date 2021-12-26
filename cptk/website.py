from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import TYPE_CHECKING, Optional, Union, List
if TYPE_CHECKING:
    from cptk import Contest, Problem
    from bs4 import BeautifulSoup


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

    @staticmethod
    @abstractmethod
    def name() -> str:
        """ The name of the website. """

    @staticmethod
    @abstractmethod
    def domain() -> Union[str, List[str]]:
        """ A single domain or a list of domains that are represented by this
        class. """

    @staticmethod
    @abstractmethod
    def is_contest(info: PageInfo) -> bool:
        """ Returns True only if the given page information describes a page
        with a contest (a collection of multiple problems). """

    @staticmethod
    @abstractmethod
    def to_contest(info: PageInfo) -> Optional['Contest']:
        """ Constructs and a Contest instance that represents the contest that
        is displayed in the given page. If the given page doesn't display a
        contest information, returns None. """

    @staticmethod
    @abstractmethod
    def is_problem(info: PageInfo) -> bool:
        """ Returns True only if the given page information describes a page
        with a single problem. """

    @staticmethod
    @abstractmethod
    def to_problem(info: PageInfo) -> Optional['Problem']:
        """ Constructs and a Problem instance that represents the problem that
        is displayed in the given page. If the given page doesn't display a
        single and unique problem, returns None. """
