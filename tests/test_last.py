import os
from typing import TYPE_CHECKING

from cptk.local import LocalProject

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy


from cptk import constants


class TestLast:

    def test_new_project(self, tempdir: 'EasyDirectory'):
        proj = LocalProject.init(tempdir.path)
        assert proj.last is None
        assert not os.path.isfile(tempdir.join(constants.LAST_FILE))

    def test_after_clone(self, tempdir: 'EasyDirectory', dummy: 'Dummy'):
        proj = LocalProject.init(tempdir.path)
        prob = proj.clone_problem(dummy.get_dummy_problem())
        assert os.path.isfile(tempdir.join(constants.LAST_FILE))
        assert proj.last == prob.location
