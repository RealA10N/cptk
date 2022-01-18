from dataclasses import dataclass, field
from urllib import parse

from cptk.scrape import Website, Test, ProblemGroup, Problem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Optional
    from cptk.scrape import PageInfo
    from bs4 import BeautifulSoup


@dataclass(unsafe_hash=True)
class CodeforecsProblem(Problem):
    mark: str = field(compare=False, default=None)
    gym: bool = field(compare=False, default=False)


class Codeforces(Website):

    @property
    def name(self) -> str:
        return 'Codeforces'

    @property
    def domain(self) -> str:
        return 'codeforces.com'

    @staticmethod
    def _parse_code_text(soup: 'BeautifulSoup') -> None:
        text = soup.text.replace('<br>', '\n').replace('\r', '').strip()
        return '\n'.join(
            line.strip()
            for line in text.splitlines(keepends=False)
        ) + '\n'

    @classmethod
    def _parse_tests(cls, info: 'PageInfo') -> 'List[Test]':
        """ Assumes that the given 'PageInfo' instance describes a Problem page,
        and parses all sample test cases in the page. """

        tests_soup = info.data.find('div', {'class': 'sample-tests'})
        for br_soup in tests_soup.find_all('br'):
            br_soup.replace_with('\n')

        inputs_soup = tests_soup.find_all('div', {'class': 'input'})
        outputs_soup = tests_soup.find_all('div', {'class': 'output'})

        return [
            Test(
                input=cls._parse_code_text(in_soup.find('pre')),
                expected=cls._parse_code_text(ex_soup.find('pre')),
            ) for in_soup, ex_soup in zip(inputs_soup, outputs_soup)
        ]

    def is_problem(self, info: 'PageInfo') -> bool:
        """ Returns 'True' if the given 'PageInfo' instance contains a problem
        statement. """
        elem = info.data.find('div', {'class': 'problem-statement'})
        return elem is not None

    def to_problem(self, info: 'PageInfo') -> 'Optional[Problem]':
        """ Assumes that the given 'PageInfo' instance contains a problem
        statement and returns a 'Problem' instance that describes the problem.
        """

        header_soup = info.data.find('div', {'class': 'header'})

        title = header_soup.find('div', {'class': 'title'}).text
        mark, name = [i.strip() for i in title.split('.')]

        group = self.to_group(info)

        gym = next(
            p.lower() == 'gym'
            for p in parse.urlparse(info.url).path.split('/')
            if p
        )

        time_limit_soup = header_soup.find('div', {'class': 'time-limit'})
        time_limit = next(
            float(word) for word in time_limit_soup.find(text=True, recursive=False).split()
            if word.strip().isnumeric()
        )

        memory_limit_soup = header_soup.find('div', {'class': 'memory-limit'})
        memory_limit = next(
            float(word) for word in memory_limit_soup.find(text=True, recursive=False).split()
            if word.strip().isnumeric()
        )

        return CodeforecsProblem(
            _uid=[group._uid, mark],
            website=self,
            name=name,
            mark=mark,
            gym=gym,
            url=info.url,
            group=group,
            tests=self._parse_tests(info),
            time_limit=time_limit,
            memory_limit=memory_limit,
        )

    def is_group(self, info: 'PageInfo') -> bool:
        """ Returns True if the given 'PageInfo' instance contains information
        of a contest. Note that the given page can also be a problem page that
        has information about the contest that the problem is taken from in the
        sidebar. """
        return self._contest_from_sidebar(info) is not None

    def to_group(self, info: 'PageInfo') -> 'Optional[ProblemGroup]':
        """ If possible, extracts information about the contest that is presented
        in the given page. If the page doesn't contain a contest information,
        returns 'None'. """
        return self._contest_from_sidebar(info)

    def _contest_from_sidebar(self, info: 'PageInfo') -> 'Optional[ProblemGroup]':
        """ Tries to pull information about the current contest using the sidebar
        information that is displayed on every page that is related to a contest.
        If fails to locate the sidebar, returns None. """

        tables = info.data.find_all('table', {'class': 'rtable'})
        links = [table.find('a', href=True) for table in tables]

        try:
            link = next(link for link in links
                        if 'contest' or 'gym'
                        in link['href'].split('/'))
        except StopIteration:
            return None

        return ProblemGroup(
            website=self,
            _uid=int(link['href'].split('/')[-1]),
            name=link.text.strip(),
            url=parse.urljoin(info.url, link['href']),
        )
