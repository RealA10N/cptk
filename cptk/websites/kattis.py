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
    # TODO: add author and source attributes.
    pass


@dataclass(unsafe_hash=True)
class KattisArchiveProblem(KattisProblem):
    difficulty: float = field(compare=True, default=None)


@dataclass(unsafe_hash=True)
class KattisContestProblem(KattisProblem):
    mark: str = field(compare=False, default=None)


@dataclass(unsafe_hash=True)
class KattisContest(Contest):
    pass


@dataclass(unsafe_hash=True)
class KattisArchive(Contest):
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
        items = text.split()[:-1]  # last element is the timezone
        time = datetime.datetime.strptime(items.pop(), '%H:%M').time()
        date = (
            datetime.date.today() if not items
            else datetime.datetime.strptime(items.pop(), '%Y-%m-%d').date()
        )
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

        active = info.data.find(
            'div', {'class': 'contest-progress session-finished'}
        ) is None

        return KattisContest(
            _uid=uid,
            url=parse.urljoin(info.url, f'/contests/{uid}'),
            website=self,
            name=name,
            start_time=st,
            end_time=et,
            active=active,
        )

    def _parse_archive(self, info: 'PageInfo') -> 'KattisArchive':
        url = parse.urlparse(info.url)
        uid = url.path.split('/')[1]
        return KattisArchive(
            uid,
            website=self,
            name=uid.title(),
            url=parse.urljoin(info.url, f'/{uid}'),
        )

    def _parse_sidebar_field(self, info: 'PageInfo', field: str) -> str:
        sidebar = info.data.find(
            'div',
            {'class': 'problem-sidebar sidebar-info'}
        )

        metadatas = sidebar.find_all('p')
        field_soup = next(
            soup for soup in metadatas
            if field in soup.text
        )

        return field_soup.text.split(':')[-1].strip()

    def to_problem(self, info: 'PageInfo') -> KattisProblem:

        title = info.data.find('div', {'class': 'headline-wrapper'}).find('h1')
        br = title.find('br')
        name = br.next_sibling.text if br else title.text

        uid = self._parse_sidebar_field(info, 'Problem ID')
        time_limit = self._parse_sidebar_field(info, 'CPU Time limit')
        memory_limit = self._parse_sidebar_field(info, 'Memory limit')

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

        else:
            archive = self._parse_archive(info)
            diff = float(self._parse_sidebar_field(info, 'Difficulty'))
            return KattisArchiveProblem(
                **kwargs,
                contest=archive,
                difficulty=diff,
            )
