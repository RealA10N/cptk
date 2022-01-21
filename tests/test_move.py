from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .utils import EasyDirectory
    from typing import Dict

import pytest

from cptk import constants
from cptk.local import LocalProject


class TestMove:

    @pytest.mark.parametrize('raw, expected', (
        (
            'code-submission-evaluation-system::cses',
            {
                'code-submission-evaluation-system': 'cses'
            },
        ),
        (
            'Codeforces.com :: Codeforces'
            'Cses.fi:: Cses',
            {
                'Codeforces.com': 'Codeforces',
                'Cses.fi': 'Cses',
            }
        )
    ))
    def test_load_moves(
        self,
        raw: str,
        expected: 'Dict[str, str]',
        tempdir: 'EasyDirectory',
    ):
        proj = LocalProject.init(tempdir.path)
        tempdir.create(constants.MOVE_FILE, raw)
        proj._load_moves() == expected

    def test_load_new_project(self, tempdir: 'EasyDirectory'):
        proj = LocalProject.init(tempdir.path)
        proj._load_moves() == {}
