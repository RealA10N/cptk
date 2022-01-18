import re
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from urllib.parse import urljoin
from urllib.parse import urlparse

from cptk.scrape import Contest
from cptk.scrape import Problem
from cptk.scrape import Test
from cptk.scrape import Website

if TYPE_CHECKING:
    from typing import Optional, List
    from cptk import PageInfo
    from bs4 import BeautifulSoup


@dataclass(unsafe_hash=True)
class CsesContest(Contest):
    pass


@dataclass(unsafe_hash=True)
class CsesContestProblem(Problem):
    mark: str = field(compare=False, default=None)


@dataclass(unsafe_hash=True)
class CsesProblemsetProblem(Problem):
    section: str = field(compare=False, default=None)


class Cses(Website):

    @property
    def name(self) -> str:
        return 'Code Submission Evaluation System'

    @property
    def domain(self) -> str:
        return 'cses.fi'

    def _contest_from_titlebar(
        self,
        info: 'PageInfo',
    ) -> 'Optional[CsesContest]':
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
            url = urljoin(info.url, title_soup.find('a')['href'])

            return CsesContest(
                website=self,
                _uid=uid,
                name=title_soup.text.strip(),
                url=url,
            )

        except (AttributeError, TypeError):
            return None

    @staticmethod
    def _parse_code_text(soup: 'BeautifulSoup') -> None:
        return soup.text.replace('<br>', '\n').replace('\r', '').strip() + '\n'

    def _parse_tests(self, info: 'PageInfo') -> 'List[Test]':
        content = info.data.find('div', {'class': 'content'})

        titles_soup = content.find_all(
            'b', {'id': re.compile('.*(example|esimerkki).*')})

        tests = list()
        for title in titles_soup:
            title: 'BeautifulSoup'

            input_soup = title.find_next_sibling('code')
            expected_soup = input_soup.find_next_sibling('code')

            tests.append(Test(
                input=self._parse_code_text(input_soup),
                expected=self._parse_code_text(expected_soup),
            ))

        return tests

    def is_problem(self, info: 'PageInfo') -> bool:
        soup = info.data.find('ul', {'class': 'task-constraints'})
        return soup is not None

    def to_problem(self, info: 'PageInfo') -> 'Optional[Problem]':
        contest = self._contest_from_titlebar(info)

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
            float(word) for word
            in time_limit_soup.find(text=True, recursive=False)
            if word.strip().isnumeric()
        )

        memory_limit_soup = time_limit_soup.find_next_sibling('li')
        memory_limit = next(
            float(word) for word
            in memory_limit_soup.find(text=True, recursive=False).split()
            if word.strip().isnumeric()
        )

        kwargs = {
            'website': self,
            '_uid': [contest._uid, uid],
            'name': name,
            'url': info.url,
            'tests': self._parse_tests(info),
            'contest': contest,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
        }

        if level is not None: return CsesContestProblem(**kwargs, mark=level)
        else: return CsesProblemsetProblem(**kwargs, section=section)
