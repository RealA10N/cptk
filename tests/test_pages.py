from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from datetime import datetime
from glob import glob
from json import load
from os import path
from typing import TYPE_CHECKING

import pytest
from bs4 import BeautifulSoup

from cptk.scrape import Website
if TYPE_CHECKING:
    from typing import Iterator


from cptk.scrape import PageInfo
from cptk.websites import (
    Codeforces,
    Cses,
    Kattis,
)

WEBSITES = {
    'codeforces': Codeforces(),
    'cses': Cses(),
    'kattis': Kattis(),
}


HERE = path.dirname(__file__)
PAGES_BASEPATH = path.join(HERE, "pages")


@dataclass
class PageTestCase:
    website: 'Website'
    info: PageInfo
    expected: dict
    configfile: str


def cases_generator() -> 'Iterator[PageTestCase]':
    """ A generator that yields 'PageTestCase' instances for all avaliable page
    test cases found in the 'pages' subdirectory. """

    for website_name, website_ins in WEBSITES.items():
        pattern = f"{PAGES_BASEPATH}/{website_name}/**/*.json"

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
                website=website_ins, info=info,
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
    def test_to_problem(self, case: PageTestCase):
        self._compare(
            asdict(case.website.to_problem(case.info)),
            case.expected
        )

    @classmethod
    def _compare(cls, obj: dict, expected: dict):
        assert set(obj.keys()) == set(expected.keys())
        for key in obj:
            if is_dataclass(obj[key]):
                cls._compare(asdict(obj[key]), expected[key])
            elif isinstance(obj[key], dict):
                cls._compare(obj[key], expected[key])
            elif isinstance(obj[key], Website):
                website: Website = obj[key]
                assert expected[key] == website.name
            elif isinstance(obj[key], datetime):
                assert expected[key] == obj[key].strftime('%Y-%m-%d %H:%M')
            else:
                assert expected[key] == obj[key]

    @pytest.mark.parametrize(
        'case',
        (
            pytest.param(
                case,
                id=path.relpath(case.configfile, PAGES_BASEPATH)
            ) for case in cases_generator()
        ),
    )
    def test_is_problem(self, case: PageTestCase):
        assert case.website.is_problem(case.info)
        for website in set(WEBSITES.values()) - {case.website}:
            assert not website.is_problem(case.info)
