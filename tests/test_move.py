import os
from typing import TYPE_CHECKING

from cptk.local.project import InvalidMoveSource

if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy
    from typing import Dict

import pytest

from cptk import constants
from cptk.local import LocalProject
from cptk.exceptions import InvalidMoveDest


class TestMove:

    @pytest.mark.parametrize('raw, expected', (
        (
            'code-submission-evaluation-system::cses',
            [
                ('code-submission-evaluation-system', 'cses'),
            ]
        ),
        (
            'Codeforces.com :: Codeforces\n'
            'Cses.fi:: Cses',
            [
                ('Codeforces.com ', ' Codeforces'),
                ('Cses.fi', ' Cses'),
            ],
        )
    ))
    def test_load_moves(
        self,
        raw: str,
        expected: 'Dict[str, str]',
        tempdir: 'EasyDirectory',
    ):
        proj = LocalProject.init(tempdir.path)
        tempdir.create(raw, constants.MOVE_FILE)
        assert proj._load_moves() == expected

    def test_load_new_project(self, tempdir: 'EasyDirectory'):
        proj = LocalProject.init(tempdir.path)
        proj._load_moves() == []

    def test_move_recorded(self, tempdir: 'EasyDirectory', dummy: 'Dummy'):
        proj = LocalProject.init(tempdir.path)
        proj.config.clone.path = 'clone'
        proj.clone_problem(dummy.get_dummy_problem())

        MOVES = [
            ('clone', 'yes'),
            ('yes', os.path.join('hello', 'there')),
        ]

        for src, dst in MOVES:
            src = proj.relative(src)
            dst = proj.relative(dst)
            proj.move(src, dst)

        assert proj._load_moves() == MOVES
        assert os.path.normpath(proj.move_relative(
            'clone')) == os.path.normpath(proj.relative('hello/there'))

    def test_move_outside_project(
        self,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ):
        dst = tempdir.path

        proj = LocalProject.init(tempdir.join('project'))
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())
        src = prob.location

        with pytest.raises(InvalidMoveDest):
            proj.move(src, dst)

    def test_move_cptk(
        self,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy',
    ):

        proj = LocalProject.init(tempdir.join('project'))
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())

        src = os.path.join(prob.location, '.cptk')
        dst = tempdir.join('project', 'clone_new')

        with pytest.raises(InvalidMoveSource):
            proj.move(src, dst)

    def test_move_project_root(
        self,
        tempdir: 'EasyDirectory',
        dummy: 'Dummy'
    ):

        proj = LocalProject.init(tempdir.join('project'))
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())

        src = os.path.join(prob.location, '.cptk')
        dst = tempdir.join('project', 'clone_new')

        with pytest.raises(InvalidMoveSource):
            proj.move(src, dst)
