import os
from typing import TYPE_CHECKING

from slugify import slugify

import cptk.scrape
from cptk.constants import DEFAULT_TESTS_FOLDER
from cptk.local import LocalProject
from cptk.local.problem import LocalProblem

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy


class TestProblemClone:

    def test_add_custom_test(self, tempdir: 'EasyDirectory', dummy: 'Dummy'):
        problem = dummy.get_dummy_problem()

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
        assert cptk.scrape.Test('hello!') in prob.tests

    def test_clone_preprocess(self, tempdir: 'EasyDirectory', dummy: 'Dummy'):
        problem = dummy.get_dummy_problem()

        proj = LocalProject.init(tempdir.path, template='g++')
        proj.config.clone.path = '{{problem.website.name}}/{{problem.name}}'

        proj.config.clone.template = tempdir.join('template')
        tempdir.create(
            '{{problem.website.name|slug}}\n{{problem.name}}',
            'template', 'temp.txt',
        )

        prob = proj.clone_problem(problem)

        loc = os.path.join(prob.location, prob.location)
        assert loc == os.path.join(
            tempdir.path, problem.website.name, problem.name)

        res = os.path.join(prob.location, 'temp.txt')
        assert os.path.isfile(res)
        with open(res, 'r') as file: data = file.read()
        assert data == f'{slugify(problem.website.name)}\n{problem.name}'
