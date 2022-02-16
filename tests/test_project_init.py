from __future__ import annotations

import os
from unittest import mock

import pytest

import cptk.constants
from .utils import EasyDirectory
from cptk.core.templates import DEFAULT_TEMPLATES
from cptk.exceptions import ProjectNotFound
from cptk.local.project import LocalProject
from cptk.utils import find_tree_files

UID_TO_TEMPLATE = {t.uid: t for t in DEFAULT_TEMPLATES}


@pytest.mark.parametrize('template', UID_TO_TEMPLATE.keys())
def test_default_init(tempdir: EasyDirectory, template: str):
    """ Tests expected behavior for init command with default args. """

    # Assert that there is no other project that can break the test
    assert not LocalProject.is_project(tempdir.path)
    with pytest.raises(ProjectNotFound):
        LocalProject.find(tempdir.path)

    proj = LocalProject.init(tempdir.path, template)

    # Assert that required files are created
    assert os.path.isfile(tempdir.join(cptk.constants.PROJECT_FILE))

    # Assert that newly created project is identifiable by cptk itself
    assert LocalProject.is_project(tempdir.path)
    assert LocalProject.find(tempdir.path) == proj
    assert LocalProject.find(tempdir.join('a/b/c')) == proj


@pytest.mark.parametrize(
    'old_template_uid, new_template_uid', (
        ('py', 'g++'),
    ),
)
def test_overwrite_existing_project(
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
    assert set(find_tree_files(old_template.path)) != set(
        find_tree_files(new_template.path),
    )

    # Initialize first project
    LocalProject.init(tempdir.path, template=old_template_uid)

    # Initialize second project
    with mock.patch(
        'cptk.core.system.System.confirm',
        mock.Mock(return_value=True),
    ) as res:
        LocalProject.init(tempdir.path, template=new_template_uid)
    res.assert_called_once()
