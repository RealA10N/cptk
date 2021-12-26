from cptk import Website, Test

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List
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
