from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cptk import PageInfo


class cptkException(Exception):
    """ Base cptk exception. All exceptions raised and created by cptk should
    inherent from this one. """


@dataclass(frozen=True)
class InvalidClone(cptkException):
    """ Raised when the clone command is called with a 'PageInfo' instance that
    doesn't describe anything that can be cloned. """

    info: 'PageInfo'


@dataclass(frozen=True)
class UnknownWebsite(cptkException):
    """ Raised when trying to fetch information from a website that is not
    registed and can't be handled by cptk. """

    domain: str