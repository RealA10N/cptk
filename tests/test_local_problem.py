import pytest
import os
from textwrap import dedent
from slugify import slugify

from cptk.local import LocalProject
from cptk.local.problem import LocalProblem
from cptk import scrape
from cptk.websites import Codeforces
from cptk.constants import DEFAULT_TESTS_FOLDER

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .utils import EasyDirectory


class TestProblemClone:

    @pytest.mark.parametrize('problem', (
        scrape.Problem(
            url='https://codeforces.com/problemset/problem/1/A',
            website=Codeforces, uid=1, name='Test Problem',
            tests=[scrape.Test('1 2', '1 2\n'), scrape.Test('1 4')],
            contest=scrape.Contest(Codeforces, 1, 'Test Contest'),
        ),
    ))
    def test_add_custom_test(
        self,
        tempdir: 'EasyDirectory',
        problem: 'scrape.Problem',
    ):

        proj = LocalProject.init(tempdir.path, template='g++')
        prob = proj.clone_problem(problem)

        tests_dir = os.path.join(prob.location, DEFAULT_TESTS_FOLDER)
        test_files = os.listdir(tests_dir)
        tests = len(problem.tests)

        assert len(test_files) == tests + \
            len([t for t in problem.tests if t.expected is not None])
        assert set(prob.tests) == set(problem.tests)

        new_test = os.path.join(tests_dir, 'in-my.txt')
        assert not os.path.exists(new_test)
        with open(new_test, 'w', encoding='utf8') as file:
            file.write('hello!')
        assert os.path.exists(new_test)

        prob = LocalProblem(prob.location)
        assert len(prob.tests) == tests + 1
        assert scrape.Test('hello!') in prob.tests

    @pytest.mark.parametrize('problem', (
        scrape.Problem(
            url='https://codeforces.com/problemset/problem/1/A',
            website=Codeforces, uid=1, name='Test Problem',
            tests=[scrape.Test('1 2', '1 2\n'), scrape.Test('1 4')],
            contest=scrape.Contest(Codeforces, 1, 'Test Contest'),
        ),
    ))
    def test_clone_preprocess(
        self,
        tempdir: 'EasyDirectory',
        problem: 'scrape.Problem',
    ):

        proj = LocalProject.init(tempdir.path, template='g++')
        proj.config.preprocess = tempdir.create(
            dedent(
                """
                from slugify import slugify
                name = slugify(problem.name)
                __all__ = ['name']
                """
            ),
            'preprocess.py'
        )

        proj.config.clone.path = '${{problem.website.name()}}/${{problem.name}}'

        proj.config.template = tempdir.join('template')
        tempdir.create('${{name}}\n${{problem.name}}', 'template', 'temp.txt')

        prob = proj.clone_problem(problem)

        loc = os.path.join(prob.location, prob.location)
        assert loc == os.path.join(
            tempdir.path, problem.website.name(), problem.name)

        res = os.path.join(prob.location, 'temp.txt')
        assert os.path.isfile(res)
        with open(res, 'r') as file: data = file.read()
        assert data == f'{slugify(problem.name)}\n{problem.name}'
