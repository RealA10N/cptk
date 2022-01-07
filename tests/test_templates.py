from os import get_terminal_size
import os
import pytest

from cptk.templates import Template, DEFAULT_TEMPLATES


class TestTemplates:

    def test_unique_uids(self):
        uids = {temp.uid for temp in DEFAULT_TEMPLATES}
        assert len(uids) == len(DEFAULT_TEMPLATES)

    @pytest.mark.parametrize('template', DEFAULT_TEMPLATES)
    def test_valid_template(self, template: Template):
        FIELDS = {'name', 'uid', 'path'}

        for field in FIELDS:
            val = getattr(template, field)
            assert isinstance(val, str)
            assert len(val) > 0

        assert os.path.exists(template.path)
        assert os.path.isdir(template.path)
