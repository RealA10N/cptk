from cptk.constants import RECIPE_NAME, CPTK_FOLDER_NAME
from cptk.utils import cached_property
from cptk.core import load_config_file

import os
from pydantic import BaseModel, validator

from typing import List


class Recipe(BaseModel):

    bake: List[str] = []
    serve: List[str]

    @validator('*', pre=True)
    @classmethod
    def string_to_commands(cls, val) -> List[str]:
        if isinstance(val, str):
            return val.split('\n')


class LocalProblem:

    def __init__(self, location: str) -> None:
        self.location = location

    @cached_property
    def recipe(self) -> Recipe:
        path = os.path.join(self.location, CPTK_FOLDER_NAME, RECIPE_NAME)
        return load_config_file(path, Recipe)
