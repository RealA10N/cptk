import pytest

from os import path
from glob import glob
from json import load
from dataclasses import dataclass
from bs4 import BeautifulSoup


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Iterator
    from cptk.scrape import Website, Test, Problem, Contest


from cptk.scrape import PageInfo
from cptk.websites import (
    Codeforces,
    Cses,
)

WEBSITES = (
    Codeforces,
    Cses,
)


HERE = path.dirname(__file__)
PAGES_BASEPATH = path.join(HERE, "pages")


@dataclass
class PageTestCase:
    website: 'Type[Website]'
    info: PageInfo
    expected: dict
    configfile: str


def cases_generator() -> 'Iterator[PageTestCase]':
    """ A generator that yields 'PageTestCase' instances for all avaliable page
    test cases found in the 'pages' subdirectory. """

    for website in WEBSITES:
        pattern = f"{PAGES_BASEPATH}/{website.name()}/**/*.json"

        for case_config in glob(pattern, recursive=True):

            # Load test case configuration from json
            with open(case_config, mode='r', encoding='utf8') as f:
                case = load(f)

            # Load html page file that is relevant to the current case
            base_path = path.dirname(case_config)
            data_path = path.join(base_path, case['info']['data'])
            with open(data_path, mode='r', encoding='utf8') as f:
                data = f.read()

            info = PageInfo(
                case['info']['url'],
                BeautifulSoup(data, 'lxml'),
            )

            yield PageTestCase(
                website=website, info=info,
                expected=case['expected'], configfile=case_config
            )


class TestPages:

    @pytest.mark.parametrize(
        'case',
        (
            pytest.param(
                case,
                id=path.relpath(case.configfile, PAGES_BASEPATH)
            ) for case in cases_generator()
        ),
    )
    def test_page(self, case: PageTestCase):
        site = case.website
        assert site.is_problem(case.info) == ('problem' in case.expected)
        assert site.is_contest(case.info) == ('contest' in case.expected)

        if 'contest' in case.expected:
            self._test_contest(
                contest=case.website.to_contest(case.info),
                expected=case.expected['contest'],
            )

        if 'problem' in case.expected:
            self._test_problem(
                problem=case.website.to_problem(case.info),
                expected=case.expected['problem'],
            )

    def _test_contest(self, contest: 'Contest', expected: dict) -> None:
        """ Asserts that the given 'Contest' instance matches the expected
        values given via the 'expected' dictionary. """
        assert contest.uid == expected['uid']
        assert contest.name == expected['name']

    def _test_problem(self, problem: 'Problem', expected: dict) -> None:
        """ Assert that the given 'Problem' instance matches the expected
        values given via the 'expected' dictionary. """

        # Test metadata
        assert problem.uid == tuple(expected['uid'])
        assert problem.name == expected['name']
        assert problem.level == expected['level']
        assert problem.section == expected['section']
        assert problem.time_limit == expected['time_limit']
        assert problem.memory_limit == expected['memory_limit']

        # Test example test cases
        assert len(problem.tests) == len(expected['tests'])
        for test, expected_test in zip(problem.tests, expected['tests']):
            test: 'Test'
            assert test.input == expected_test['input']
            assert test.expected == expected_test['expected']

        # Test parent contest
        if problem.contest:
            self._test_contest(
                contest=problem.contest,
                expected=expected['contest'],
            )
