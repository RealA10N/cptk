import pkg_resources
from urllib.parse import urlparse

from dataclasses import dataclass
from cptk.exceptions import cptkException

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from cptk import Website, PageInfo, Contest, Problem


@dataclass
class InvalidClone(cptkException):
    """ Raised when the clone command is called with a 'PageInfo' instance that
    doesn't describe anything that can be cloned. """

    info: 'PageInfo'


@dataclass
class UnknownWebsite(cptkException):
    """ Raised when trying to fetch information from a website that is not
    registed and can't be handled by cptk. """

    domain: str


class Integrator:

    def __init__(self) -> None:
        self._load_websites()

    def _load_websites(self) -> List['Website']:
        self._websites = [
            point.load()
            for point in pkg_resources.iter_entry_points('cptk_sites')
        ]

        self._domain_to_website = dict()
        for website in self._websites:
            domain = website.domain()
            if isinstance(domain, str):
                self._domain_to_website[domain] = website
            else:
                for cur in domain:
                    self._domain_to_website[cur] = website

    # --------------------------------------------------------------- Clone -- #

    def clone_webpage(self, info: 'PageInfo') -> None:
        """ Recives an arbitrary page info instance and tries to match it with
        a Website class that knows how to handle this specific website. If cptk
        doesn't find a way to parse the given webpage, it raises the
        'InvalidClone' exception. """

        domain = urlparse(info.url).netloc
        website = self._domain_to_website.get(domain)

        if website is None:
            raise UnknownWebsite(domain)

        elif website.is_problem(info):
            return self.clone_problem(website.to_problem(info))

        elif website.is_contest(info):
            return self.clone_contest(website.to_contest(info))

        raise InvalidClone(info)

    def clone_contest(self, contest: 'Contest') -> None:
        """ Clones the given contest and every problem in to. """
        raise NotImplementedError  # TODO implement clone_contest method

    def clone_problem(self, problem: 'Problem') -> None:
        """ Clones the given problem. """
        raise NotImplementedError  # TODO implement clone_problem method
