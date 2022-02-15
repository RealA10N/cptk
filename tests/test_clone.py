import os
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy

import pytest
from slugify import slugify
from freezegun import freeze_time
from filecmp import dircmp

import cptk.scrape
import cptk.constants
from cptk.local.project import LocalProject
from cptk.local.problem import LocalProblem
from cptk.core.templates import DEFAULT_TEMPLATES
from cptk.core.templates import Template


HERE = os.path.dirname(__file__)
CLONES_DIR = os.path.join(HERE, 'clones')
TEMPLATE = DEFAULT_TEMPLATES[0].uid


@mock.patch('os.getlogin', lambda: 'User')
@freeze_time('2022-01-01')
class TestProblemClone:

    def test_clone_preprocess(self, tempdir: 'EasyDirectory', dummy: 'Dummy'):
        problem = dummy.get_dummy_problem()

        proj = LocalProject.init(tempdir.path, TEMPLATE)
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

    @classmethod
    def _compare_files(cls, src: str, dst: str) -> None:
        with open(src, 'r') as file:
            src_data = file.read()
        with open(dst, 'r') as file:
            dst_data = file.read()
        assert src_data == dst_data

    @classmethod
    def _assert_equal_dirs(cls, src: str, dst: str) -> None:
        res = dircmp(src, dst)
        assert not res.left_only and not res.right_only
        for filename in res.diff_files:
            # For a detailed message error, we compare the files ourselves.
            cls._compare_files(
                os.path.join(src, filename),
                os.path.join(dst, filename),
            )
        for common in res.common_dirs:
            cls._assert_equal_dirs(os.path.join(
                src, common), os.path.join(dst, common))

    def _assert_valid_problem(self, path: str) -> None:
        """ Checks that given path and asserts that the path contains a
        well-defined problem. """

        assert LocalProblem.is_problem(path)
        recipe_path = os.path.join(path, cptk.constants.RECIPE_FILE)
        assert os.path.isfile(recipe_path)

    @mock.patch('platform.system', lambda: 'Linux')
    @pytest.mark.parametrize('template', (
        pytest.param(template, id=template.uid)
        for template in DEFAULT_TEMPLATES
    ))
    def test_default_templates(
        self,
        tempdir: 'EasyDirectory',
        template: 'Template',
        dummy: 'Dummy',
    ):
        name = template.uid
        proj = LocalProject.init(tempdir.path, template=name)
        proj.config.clone.path = 'clone'
        prob = proj.clone_problem(dummy.get_dummy_problem())
        self._assert_equal_dirs(tempdir.join(
            'clone'), os.path.join(CLONES_DIR, name))
        self._assert_valid_problem(prob.location)

    @mock.patch('platform.system', lambda: 'Windows')
    @pytest.mark.parametrize('template', (
        pytest.param(template, id=template.uid)
        for template in DEFAULT_TEMPLATES
    ))
    def test_default_templates_win(
        self,
        tempdir: 'EasyDirectory',
        template: 'Template',
        dummy: 'Dummy',
    ):
        name = template.uid
        expected = os.path.join(CLONES_DIR, f'win-{name}')
        proj = LocalProject.init(tempdir.path, template=name)
        proj.config.clone.path = 'clone'
        prob = proj.clone_problem(dummy.get_dummy_problem())
        self._assert_equal_dirs(tempdir.join('clone'), expected)
        self._assert_valid_problem(prob.location)
