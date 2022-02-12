import os
from filecmp import dircmp

import pytest

import cptk.constants
from .utils import EasyDirectory
from cptk.core.templates import DEFAULT_TEMPLATES
from cptk.exceptions import ProjectNotFound
from cptk.local.project import LocalProject


UID_TO_TEMPLATE = {t.uid: t for t in DEFAULT_TEMPLATES}


class TestProjectInit:

    def test_default_init(self, tempdir: EasyDirectory):
        """ Tests expected behavior for init command with default args. """

        # Assert that there is no other project that can break the test
        assert not LocalProject.is_project(tempdir.path)
        with pytest.raises(ProjectNotFound):
            LocalProject.find(tempdir.path)

        proj = LocalProject.init(tempdir.path)

        # Assert that required files are created
        assert os.path.isfile(tempdir.join(cptk.constants.PROJECT_FILE))

        # Assert that newly created project is identifiable by cptk itself
        assert LocalProject.is_project(tempdir.path)
        assert LocalProject.find(tempdir.path) == proj
        assert LocalProject.find(tempdir.join('a/b/c')) == proj

        template = tempdir.join(cptk.constants.DEFAULT_TEMPLATE_FOLDER)
        assert os.path.isdir(template)
        assert os.listdir(template) == []

    @pytest.mark.parametrize('old_template_uid, new_template_uid', (
        ('py', 'g++'),
    ))
    def test_overwrite_existing_project(
        self,
        tempdir: EasyDirectory,
        old_template_uid: str,
        new_template_uid: str,
    ):
        """ Tests for expected behavior if user tries to initialize a cptk
        project inside an already initialized one. """

        old_template = UID_TO_TEMPLATE.get(old_template_uid)
        new_template = UID_TO_TEMPLATE.get(new_template_uid)

        # Assert that those are valid templates
        assert old_template is not None and new_template is not None

        # Assert that there are differences between the templates
        res = dircmp(old_template.path, new_template.path)
        assert res.left_only or res.right_only or res.diff_files

        # Initialize two projects one after another
        LocalProject.init(tempdir.path, template=old_template_uid)
        LocalProject.init(tempdir.path, template=new_template_uid)

        template_loc = tempdir.join(cptk.constants.DEFAULT_TEMPLATE_FOLDER)
        template_src = new_template.path

        # Assert that the new template replaced the old one
        res = dircmp(template_loc, template_src)
        assert not res.left_only and not res.right_only and not res.diff_files
