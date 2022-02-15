import os
from typing import TYPE_CHECKING

import cptk.constants
from cptk.core.templates import DEFAULT_TEMPLATES
from cptk.local.project import LocalProject

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy

TEMPLATE = DEFAULT_TEMPLATES[0].uid


def test_new_project(tempdir: 'EasyDirectory'):
    proj = LocalProject.init(tempdir.path, TEMPLATE)
    assert proj.last() is None
    assert not os.path.isfile(tempdir.join(cptk.constants.LAST_FILE))


def test_after_clone(tempdir: 'EasyDirectory', dummy: 'Dummy'):
    proj = LocalProject.init(tempdir.path, TEMPLATE)
    prob = proj.clone_problem(dummy.get_dummy_problem())
    assert os.path.isfile(tempdir.join(cptk.constants.LAST_FILE))
    assert prob == proj.last()
