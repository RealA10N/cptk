from cptk import Website, Test, Contest

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Optional
    from cptk import PageInfo


class Codeforces(Website):

    @staticmethod
    def name():
        return 'Codeforces'

    @staticmethod
    def domain() -> 'List[str]':
        return [
            'codeforces.com',
            'm1.codeforces.com',
            'm2.codeforces.com',
            'm3.codeforces.com',
        ]

    @staticmethod
    def _parse_tests(info: 'PageInfo') -> 'List[Test]':
        """ Assumes that the given 'PageInfo' instance describes a Problem page,
        and parses all sample test cases in the page. """

        tests_soup = info.data.find('div', {'class': 'sample-tests'})
        for br_soup in tests_soup.find_all('br'):
            br_soup.replace_with('\n')

        inputs_soup = tests_soup.find_all('div', {'class': 'input'})
        outputs_soup = tests_soup.find_all('div', {'class': 'output'})

        return [
            Test(
                input=input.find('pre').text,
                expected=output.find('pre').text
            ) for input, output in zip(inputs_soup, outputs_soup)
        ]

    @staticmethod
    def is_problem(info: 'PageInfo') -> bool:
        """ Returns 'True' if the given 'PageInfo' instance contains a problem
        statement. """
        elem = info.data.find('div', {'class': 'problem-statement'})
        return elem is not None

    @classmethod
    def is_contest(cls, info: 'PageInfo') -> bool:
        """ Returns True if the given 'PageInfo' instance contains information
        of a contest. Note that the given page can also be a problem page that
        has information about the contest that the problem is taken from in the
        sidebar. """
        return cls._contest_from_sidebar(info) is not None

    @classmethod
    def to_contest(cls, info: 'PageInfo') -> 'Optional[Contest]':
        """ If possible, extracts information about the contest that is presented
        in the given page. If the page doesn't contain a contest information,
        returns 'None'. """
        return cls._contest_from_sidebar(info)

    @classmethod
    def _contest_from_sidebar(cls, info: 'PageInfo') -> 'Optional[Contest]':
        """ Tries to pull information about the current contest using the sidebar
        information that is displayed on every page that is related to a contest.
        If fails to locate the sidebar, returns None. """

        tables = info.data.find_all('table', {'class': 'rtable'})
        links = [table.find('a', href=True) for table in tables]

        try:
            link = next(link for link in links
                        if 'contest' in link['href'].split('/'))
        except StopIteration:
            return None

        return Contest(
            website=cls,
            uid=int(link['href'].split('/')[-1]),
            name=link.text.strip(),
        )
