import os
from filecmp import dircmp
from unittest import mock

import pytest
from freezegun import freeze_time

from .utils import Dummy
from .utils import EasyDirectory
from cptk.core import Preprocessor
from cptk.local import LocalProject
from cptk.templates import DEFAULT_TEMPLATES
from cptk.templates import Template

HERE = os.path.dirname(__file__)
CLONES_DIR = os.path.join(HERE, 'clones')
EXPECTED_CLONES = {
    name: os.path.join(CLONES_DIR, name)
    for name in os.listdir(CLONES_DIR)
}


class TestPreprocessor:

    @pytest.mark.parametrize('template, expected', (
        ('{{invalid}}', ''),
        ('{{invalid|slug}}', ''),
        ('{{invalid|invalid}}', ''),
        ('{{problem.name}}', 'name'),
    ))
    def test_invalid_input(
        self,
        template: str,
        expected: str,
        dummy: 'Dummy',
    ):
        prob = dummy.get_dummy_problem()
        prob.name = 'name'

        pre = Preprocessor(prob)
        assert pre.parse_string(template) == expected

    @classmethod
    def _assert_equal_dirs(cls, src: str, dst: str) -> None:
        res = dircmp(src, dst)
        assert not res.left_only and not res.right_only and not res.diff_files
        for common in res.common_dirs:
            cls._assert_equal_dirs(os.path.join(
                src, common), os.path.join(dst, common))

    @pytest.mark.parametrize('template', DEFAULT_TEMPLATES)
    @mock.patch('os.getlogin', lambda: 'User')
    @freeze_time('2022-01-01')
    def test_default_templates(
        self,
        tempdir: 'EasyDirectory',
        template: 'Template',
        dummy: 'Dummy',
    ):
        name = template.uid
        expected = EXPECTED_CLONES[name]
        proj = LocalProject.init(tempdir.path, template=name)
        proj.config.clone.path = 'clone'
        proj.clone_problem(dummy.get_dummy_problem())
        self._assert_equal_dirs(tempdir.join('clone'), expected)
