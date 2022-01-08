import pytest

import os
import stat

from .utils import requires, EasyDirectory

from cptk.local import LocalProject
from cptk.exceptions import SystemRunError


class TestProjectInit:

    @requires('git')
    def test_git(self, tempdir: EasyDirectory) -> None:
        proj = LocalProject.init(location=tempdir.path, git=True)

        assert proj.config.git
        assert os.path.isdir(tempdir.join('.git'))

    @requires('git')
    def test_git_fail(self, tempdir: EasyDirectory) -> None:

        # mask out read and write owner permissions
        mask = ~(stat.S_IRUSR | stat.S_IWUSR)
        mode = os.stat(tempdir.path).st_mode
        os.chmod(tempdir.path, mode=mode & mask)

        with pytest.raises(SystemRunError):
            LocalProject.init(location=tempdir.path, git=True)

        # Change permissions back to normal, avoid warnings and errors
        os.chmod(tempdir.path, mode)
