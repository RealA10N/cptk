import re
from os import path

import pytest

from cptk.constants import RECIPE_FILE
from cptk.local.problem import RecipeConfig
from cptk.templates import DEFAULT_TEMPLATES
from cptk.templates import Template


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

        assert re.fullmatch(r'[a-z0-9\-_+*]+', template.uid)

        assert path.isdir(template.path)

        recipe_path = path.join(template.path, RECIPE_FILE)
        assert path.isfile(recipe_path)

        # Assert that loads recipe config file without exceptions
        RecipeConfig.load(recipe_path)
