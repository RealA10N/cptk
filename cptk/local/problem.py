from os import path
from glob import glob

from pydantic import validator
from typing import List

from cptk import Test
from cptk.constants import RECIPE_FILE, DEFAULT_TESTS_FOLDER
from cptk.utils import cached_property
from cptk.core import Configuration


class Recipe(Configuration):

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
        p = path.join(self.location, RECIPE_FILE)
        return Recipe.load(p)

    @cached_property
    def tests(self) -> List[Test]:
        base = path.join(self.location, DEFAULT_TESTS_FOLDER)

        l = list()
        inputs = glob(path.join(base, '*.in'))
        for inp in inputs:

            filename = path.basename(inp)
            name = filename.split('.')[:-3]
            out = path.join(base, f'{name}.out')

            # Load input and output files

            with open(inp, 'r', encoding='utf8') as file:
                inp_data = file.read()

            try:
                with open(out, mode='r', encoding='utf8') as file:
                    out_data = file.read()
            except FileNotFoundError:
                out_data = None

            l.append(Test(inp_data, out_data))

        return l
