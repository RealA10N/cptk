import pkg_resources
from urllib.parse import urlparse
from cptk.scrape import website

from cptk.utils import cptkException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, List
    from cptk import Website, PageInfo, Element


class InvalidClone(cptkException):
    """ Raised when the clone command is called with a 'PageInfo' instance that
    doesn't describe anything that can be cloned. """

    def __init__(self, info: 'PageInfo') -> None:
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
        self._load_websites()

    def _load_websites(self) -> 'List[Type[Website]]':
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

    def _url_to_website(self, url: str) -> 'Type[Website]':
        """ Tries to convert the given url into a Website object.
        Raises an error if the URL doesn't match with any registered website."""

        domain = urlparse(url).netloc
        website = self._domain_to_website.get(domain)

        if website is None:
            raise UnknownWebsite(domain)

        return website

    def to_model(self, info: 'PageInfo') -> 'Element':
        """ Recives an arbitrary page info instance and tries to match it with
        a Website class that knows how to handle this specific website. If cptk
        doesn't find a way to parse the given webpage, it raises the
        'InvalidClone' exception. """

        website = self._url_to_website(info.url)

        if website.is_problem(info):
            return website.to_problem(info)

        if website.is_contest(info):
            return website.to_contest(info)

        raise InvalidClone(info)
