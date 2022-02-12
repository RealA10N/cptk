from typing import TYPE_CHECKING

import pkg_resources
from bs4 import BeautifulSoup
from requests import session

from cptk.scrape import PageInfo
from cptk.scrape import Website
from cptk.utils import cptkException

if TYPE_CHECKING:
    from typing import Type, List
    from cptk.scrape import Problem


class InvalidClone(cptkException):
    """ Raised when the clone command is called with a 'PageInfo' instance that
    doesn't describe anything that can be cloned. """

    def __init__(self, info: PageInfo) -> None:
        self.info = info
        super().__init__(f"We don't know how to handle data from {info.url!r}")


class UnknownWebsite(cptkException):
    """ Raised when trying to fetch information from a website that is not
    registed and can't be handled by cptk. """

    def __init__(self, domain: str) -> None:
        self.domain = domain
        super().__init__(f"We don't know how to handle data from {domain!r}")


class Fetcher:

    def __init__(self) -> None:
        self.session = session()
        self._load_websites()

    def _load_websites(self) -> 'List[Type[Website]]':
        self._websites = [
            point.load()()
            for point in pkg_resources.iter_entry_points('cptk_sites')
        ]

        self._domain_to_website = dict()
        for website in self._websites:
            domain = website.domain
            if isinstance(domain, str):
                self._domain_to_website[domain] = website
            else:
                for cur in domain:
                    self._domain_to_website[cur] = website

    def page_to_problem(self, info: PageInfo) -> 'Problem':
        """ Recives an arbitrary page info instance and tries to match it with
        a Website class that knows how to handle this specific website. If cptk
        doesn't find a way to parse the given webpage, it raises the
        'InvalidClone' exception. """

        for website in self._websites:
            if website.is_problem(info):
                return website.to_problem(info)
        raise InvalidClone(info)

    def to_page(self, url: str) -> PageInfo:
        """ Makes an get http/s request to the given URL and returns the result
        as a PageInfo instance. """

        if not url.startswith('http'):
            url = f'http://{url}'

        res = self.session.get(url)
        data = BeautifulSoup(res.content, 'lxml')
        return PageInfo(url, data)
