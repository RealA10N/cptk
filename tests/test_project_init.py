import pytest

import os
import stat
from filecmp import dircmp

from .utils import run, requires, EasyDirectory

from cptk.local import LocalProject
from cptk.exceptions import SystemRunError, ProjectNotFound
from cptk.templates import DEFAULT_TEMPLATES
from cptk.constants import (
    DEFAULT_PREPROCESS,
    DEFAULT_TEMPLATE_FOLDER,
    PROJECT_FILE,
)


UID_TO_TEMPLATE = {t.uid: t for t in DEFAULT_TEMPLATES}


class TestProjectInit:

    def test_default_init(self, tempdir: EasyDirectory):
        """ Tests expected behavior for init command with default arguments. """

        # Assert that there is no other project that can break the test
        assert not LocalProject.is_project(tempdir.path)
        with pytest.raises(ProjectNotFound):
            LocalProject.find(tempdir.path)

        proj = LocalProject.init(tempdir.path)

        # Assert that required files are created
        assert os.path.isfile(tempdir.join(PROJECT_FILE))

        # Assert that newly created project is identifiable by cptk itself
        assert LocalProject.is_project(tempdir.path)
        assert LocalProject.find(tempdir.path) == proj
        assert LocalProject.find(tempdir.join('a/b/c')) == proj

        template = tempdir.join(DEFAULT_TEMPLATE_FOLDER)
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
    ) -> None:
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

        template_loc = tempdir.join(DEFAULT_TEMPLATE_FOLDER)
        template_src = new_template.path

        # Assert that the new template replaced the old one
        res = dircmp(template_loc, template_src)
        assert not res.left_only and not res.right_only and not res.diff_files

    @requires('git')
    def test_git(self, tempdir: EasyDirectory) -> None:
        """ Tests that a git repository is actually created as expected. """
        proj = LocalProject.init(location=tempdir.path, git=True)

        assert proj.config.git
        assert os.path.isdir(tempdir.join('.git'))

    @requires('git')
    @pytest.mark.parametrize('create_with_git', (True, False))
    def test_already_git_repo(
        self,
        tempdir: EasyDirectory,
        create_with_git: bool,
    ) -> None:
        """ Test that everything is ok if user tries to initialize a cptk
        project inside a git repository. """

        res = run(f'git init {tempdir.path}')
        assert res.returncode == 0

        proj = LocalProject.init(tempdir.path, git=create_with_git)
        assert proj.config.git == create_with_git

    @pytest.mark.skipif(
        os.name == 'nt',
        reason="chmod doesn't work property on Windows."
    )
    @requires('git')
    def test_git_fail(self, tempdir: EasyDirectory) -> None:
        """ Tests that the currect errors are raised if the creating of a git
        repository fails. """

        # mask out read and write owner permissions
        mask = ~(stat.S_IWRITE | stat.S_IREAD)
        mode = os.stat(tempdir.path).st_mode
        os.chmod(tempdir.path, mode=mode & mask)

        with pytest.raises(SystemRunError):
            LocalProject.init(location=tempdir.path, git=True)

        # Change permissions back to normal, avoid warnings and errors
        os.chmod(tempdir.path, mode)

    def test_default_preprocess_creation(self, tempdir: 'EasyDirectory') -> None:
        proj = LocalProject.init(tempdir.path)
        assert proj.config.preprocess == DEFAULT_PREPROCESS
        assert os.path.isfile(tempdir.join(DEFAULT_PREPROCESS))
