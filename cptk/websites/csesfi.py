from cptk import Website, Contest
from urllib.parse import urlparse

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from cptk import PageInfo


class CsesFi(Website):

    @staticmethod
    def name() -> str:
        return 'cses.fi'

    @staticmethod
    def domain() -> str:
        return 'cses.fi'

    @classmethod
    def is_contest(cls, info: 'PageInfo') -> bool:
        return cls._contest_from_titlebar(info) is not None

    @classmethod
    def to_contest(cls, info: 'PageInfo') -> 'Optional[Contest]':
        return cls._contest_from_titlebar(info)

    @classmethod
    def _contest_from_titlebar(cls, info: 'PageInfo') -> 'Optional[Contest]':
        titlebar_soup = info.data.find('div', {'class': 'title-block'})

        url = urlparse(info.url)
        try:
            uid = next(
                p for p in url.path.split('/')
                if p.strip()
            )
        except StopIteration:
            return None

        try:
            title_soup = titlebar_soup.find('h3')

            return Contest(
                website=cls,
                uid=uid,
                name=title_soup.text.strip(),
            )

        except (AttributeError, TypeError):
            return None
