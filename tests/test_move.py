from __future__ import annotations

import os
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .utils import EasyDirectory, Dummy

import pytest

import cptk.constants
from cptk.local.project import LocalProject
from cptk.exceptions import InvalidMoveDest
from cptk.local.project import InvalidMoveSource
from cptk.core.templates import DEFAULT_TEMPLATES

TEMPLATE = DEFAULT_TEMPLATES[0].uid


class TestMove:

    @pytest.mark.parametrize(
        'raw, expected', (
            (
                'code-submission-evaluation-system::cses',
                [
                    ('code-submission-evaluation-system', 'cses'),
                ],
            ),
            (
                'Codeforces.com :: Codeforces\n'
                'Cses.fi:: Cses',
                [
                    ('Codeforces.com ', ' Codeforces'),
                    ('Cses.fi', ' Cses'),
                ],
            ),
        ),
    )
    def test_load_moves(
        self,
        raw: str,
        expected: dict[str, str],
        tempdir: EasyDirectory,
    ):
        proj = LocalProject.init(tempdir.path, TEMPLATE)
        tempdir.create(raw, cptk.constants.MOVE_FILE)
        assert proj._load_moves() == expected

    def test_load_new_project(self, tempdir: EasyDirectory):
        proj = LocalProject.init(tempdir.path, TEMPLATE)
        proj._load_moves() == []

    def test_move_recorded(self, tempdir: EasyDirectory, dummy: Dummy):
        proj = LocalProject.init(tempdir.path, TEMPLATE)
        proj.config.clone.path = 'clone'
        proj.clone_problem(dummy.get_dummy_problem())

        MOVES = [
            ('clone', 'yes'),
            ('yes', os.path.join('hello', 'there')),
        ]

        for src, dst in MOVES:
            proj.move(proj.relative(src), proj.relative(dst))

        assert proj._load_moves() == MOVES
        assert os.path.normpath(
            proj.move_relative(
                'clone',
            ),
        ) == os.path.normpath(proj.relative('hello/there'))

    def test_move_outside_project(
        self,
        tempdir: EasyDirectory,
        dummy: Dummy,
    ):
        dst = tempdir.path

        proj = LocalProject.init(tempdir.join('project'), TEMPLATE)
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())
        src = prob.location

        with pytest.raises(InvalidMoveDest):
            proj.move(src, dst)

    def test_move_cptk(
        self,
        tempdir: EasyDirectory,
        dummy: Dummy,
    ):

        proj = LocalProject.init(tempdir.join('project'), TEMPLATE)
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())

        src = os.path.join(prob.location, '.cptk')
        dst = tempdir.join('project', 'clone_new')

        with pytest.raises(InvalidMoveSource):
            proj.move(src, dst)

    def test_move_project_root(
        self,
        tempdir: EasyDirectory,
        dummy: Dummy,
    ):

        proj = LocalProject.init(tempdir.join('project'), TEMPLATE)
        proj.config.clone.path = 'clone'

        prob = proj.clone_problem(dummy.get_dummy_problem())

        src = os.path.join(prob.location, '.cptk')
        dst = tempdir.join('project', 'clone_new')

        with pytest.raises(InvalidMoveSource):
            proj.move(src, dst)
