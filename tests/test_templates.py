from os import path
import pytest

from cptk.templates import Template, DEFAULT_TEMPLATES
from cptk.constants import CPTK_FOLDER_NAME, RECIPE_NAME

from cptk.local.problem import Recipe
from cptk.core import load_config_file


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

        assert path.isdir(template.path)

        cptk_dir = path.join(template.path, CPTK_FOLDER_NAME)
        assert path.isdir(cptk_dir)

        recipe_path = path.join(cptk_dir, RECIPE_NAME)
        assert path.isfile(recipe_path)

        # Assert that loads recipe config file without exceptions
        load_config_file(recipe_path, Recipe)
