import re
from types import ClassMethodDescriptorType
from urllib.parse import urlparse
from cptk import Website, Contest, Problem, Test

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, List
    from cptk import PageInfo
    from bs4 import BeautifulSoup


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

    @staticmethod
    def _parse_code_text(soup: 'BeautifulSoup') -> None:
        return soup.text.replace('<br>', '\n').replace('\r', '').strip() + '\n'

    @classmethod
    def _parse_tests(cls, info: 'PageInfo') -> 'List[Test]':
        content = info.data.find('div', {'class': 'content'})

        titles_soup = content.find_all(
            'b', {'id': re.compile('.*(example|esimerkki).*')})

        tests = list()
        for title in titles_soup:
            title: 'BeautifulSoup'

            input_soup = title.find_next_sibling('code')
            expected_soup = input_soup.find_next_sibling('code')

            tests.append(Test(
                input=cls._parse_code_text(input_soup),
                expected=cls._parse_code_text(expected_soup),
            ))

        return tests

    @classmethod
    def is_problem(cls, info: 'PageInfo') -> bool:
        soup = info.data.find('ul', {'class': 'task-constraints'})
        return soup is not None

    @classmethod
    def to_problem(cls, info: 'PageInfo') -> 'Optional[Problem]':
        contest = cls.to_contest(info)

        title_soup = info.data.find('div', {'class': 'title-block'})
        content_soup = info.data.find('div', {'class': 'content'})
        sidebar_soup = info.data.find('div', {'class': 'nav sidebar'})
        current_soup = sidebar_soup.find('a', {'class': 'current'})
        constrains_soup = content_soup.find(
            'ul', {'class': 'task-constraints'})

        uid_soup = content_soup.find('input', {'name': 'task'})
        uid = int(uid_soup['value'])

        level_soup = current_soup.find('b')
        level = level_soup.text.strip() if level_soup is not None else None

        name = title_soup.find('h1').text.strip()

        section_soup = sidebar_soup.find('h4')
        section = section_soup.text.strip()

        time_limit_soup = constrains_soup.find('li')
        time_limit = next(
            float(word) for word in time_limit_soup.find(text=True, recursive=False)
            if word.strip().isnumeric()
        )

        memory_limit_soup = time_limit_soup.find_next_sibling('li')
        memory_limit = next(
            float(word) for word in memory_limit_soup.find(text=True, recursive=False).split()
            if word.strip().isnumeric()
        )

        return Problem(
            website=cls,
            uid=(contest.uid, uid),
            name=name,
            tests=cls._parse_tests(info),
            contest=contest,
            level=level,
            section=section if level is None else None,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )
