import pkg_resources
from requests import session
from bs4 import BeautifulSoup

from typing import Type, List

from cptk.utils import cptkException
from cptk.scrape import Website, PageInfo, Element


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

    def _load_websites(self) -> List[Type[Website]]:
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

    def page_to_model(self, info: PageInfo) -> Element:
        """ Recives an arbitrary page info instance and tries to match it with
        a Website class that knows how to handle this specific website. If cptk
        doesn't find a way to parse the given webpage, it raises the
        'InvalidClone' exception. """

        for website in self._websites:
            if website.is_problem(info):
                return website.to_problem(info)
            if website.is_contest(info):
                return website.to_contest(info)

        raise InvalidClone(info)

    def to_page(self, url: str) -> PageInfo:
        """ Makes an get http/s request to the given URL and returns the result
        as a PageInfo instance. """

        res = self.session.get(url)
        data = BeautifulSoup(res.content)
        return PageInfo(url, data)

    def url_to_model(self, url: str) -> Element:
        """ Makes a get http/s request to the given URL, scraps the information
        in the page and load it as a Problem/Contest instance. Raises an error
        if cptk and it's plugins doesn't find a way to parse the given page. """
        return self.page_to_model(self.to_page(url))
