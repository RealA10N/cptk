import datetime
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from urllib import parse

from cptk.scrape import Contest
from cptk.scrape import Problem
from cptk.scrape import Test
from cptk.scrape import Website

if TYPE_CHECKING:
    from cptk.scrape import PageInfo
    from bs4 import BeautifulSoup
    from typing import List, Optional


@dataclass(unsafe_hash=True)
class KattisProblem(Problem):
    # TODO: add difficulty, author and source attributes.
    pass


@dataclass(unsafe_hash=True)
class KattisContestProblem(KattisProblem):
    mark: str = field(compare=False, default=None)


@dataclass(unsafe_hash=True)
class KattisContest(Contest):
    pass


class Kattis(Website):

    @property
    def name(self) -> str:
        return 'Kattis'

    @property
    def domain(self) -> str:
        return 'open.kattis.com'

    def is_problem(self, info: 'PageInfo') -> bool:
        return info.data.find('div', {'class': 'problem-wrapper'}) is not None

    @staticmethod
    def _parse_code_text(soup: 'BeautifulSoup') -> None:
        text = soup.text.replace('<br>', '\n').replace('\r', '').strip()
        return '\n'.join(
            line.strip()
            for line in text.splitlines(keepends=False)
        ) + '\n'

    @classmethod
    def _parse_tests(cls, info: 'PageInfo') -> 'List[Test]':

        tables = info.data.find_all('table', {'class': 'sample'})
        res = list()

        for table in tables:
            inp, out = table.find_all('pre')
            res.append(
                Test(
                    input=cls._parse_code_text(inp),
                    expected=cls._parse_code_text(out)
                )
            )

        return res

    def _parse_date(self, text: str) -> datetime.datetime:
        items = text.split()
        _ = items.pop()  # timezone
        time = datetime.time.fromisoformat(items.pop())
        date = (datetime.date.today() if not items
                else datetime.date.fromisoformat(items.pop()))
        return datetime.datetime.combine(date, time)

    def _parse_contest(self, info: 'PageInfo') -> 'Optional[KattisContest]':

        section = info.data.find('div', {'class': 'info upper'})
        if section is None: return None

        name = section.find('h2', {'class': 'title'}).text.strip()

        divs = section.find_all('div')
        start = divs[0].find('h4').next_sibling.text.strip()
        end = divs[-1].find('h4').next_sibling.text.strip()

        st = self._parse_date(start)
        et = self._parse_date(end)

        url = parse.urlparse(info.url)
        uid = url.path.split('/')[2]

        return KattisContest(
            _uid=uid,
            url=parse.urljoin(info.url, f'/contests/{uid}'),
            website=self,
            name=name,
            start_time=st,
            end_time=et,
            active=st <= datetime.datetime.now() <= et,
        )

    def to_problem(self, info: 'PageInfo') -> KattisProblem:

        sidebar = info.data.find(
            'div',
            {'class': 'problem-sidebar sidebar-info'}
        )

        title = info.data.find('div', {'class': 'headline-wrapper'}).find('h1')
        br = title.find('br')
        name = br.next_sibling.text if br else title.text

        metadatas = sidebar.find_all('p')

        uid_soup = next(
            soup for soup in metadatas
            if 'Problem ID' in soup.text
        )

        _, uid = uid_soup.text.split(':')

        time_limit_soup = next(
            soup for soup in metadatas
            if 'CPU Time limit' in soup.text
        )

        _, time_limit = time_limit_soup.text.split(':')

        memory_limit_soup = next(
            soup for soup in metadatas
            if 'Memory limit' in soup.text
        )
        _, memory_limit = memory_limit_soup.text.split(':')

        kwargs = {
            '_uid': uid.strip(),
            'website': self,
            'name': name.strip(),
            'url': info.url,
            'tests': self._parse_tests(info),
            'time_limit': int(time_limit.split()[0]),
            'memory_limit': int(memory_limit.split()[0]),
        }

        contest = self._parse_contest(info)

        if contest:
            problem_title = next(title.children)
            mark = problem_title.text.split()[-1]

            return KattisContestProblem(
                **kwargs,
                contest=contest,
                mark=mark.strip(),
            )

        return KattisProblem(**kwargs)
