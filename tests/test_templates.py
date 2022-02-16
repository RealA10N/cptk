from __future__ import annotations

from cptk.core.templates import DEFAULT_TEMPLATES


class TestTemplates:

    def test_unique_uids(self):
        uids = {temp.uid for temp in DEFAULT_TEMPLATES}
        assert len(uids) == len(DEFAULT_TEMPLATES)
