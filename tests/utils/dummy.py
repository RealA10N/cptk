from __future__ import annotations

import cptk.scrape
import cptk.websites


class Dummy:

    def __init__(self) -> None:
        self._website = cptk.websites.Codeforces()
        self._problem = cptk.scrape.Problem(
            _uid=1,
            website=self._website,
            url='https://codeforces.com/problemset/problem/1/A',
            name='Test Problem',
            tests=[cptk.scrape.Test('1 2', '1 2\n'), cptk.scrape.Test('1 4')],
            contest=cptk.scrape.Contest(
                _uid=1,
                website=self._website,
                url='https://codeforces.com/problemset',
                name='Test Contest',
            ),
        )

    def get_dummy_problem(self) -> cptk.scrape.Problem:
        return self._problem

    def get_dummy_website(self) -> cptk.scrape.Website:
        return self._website
