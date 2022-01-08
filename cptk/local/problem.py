import re
from os import path
from glob import glob
from dataclasses import dataclass, field

from pydantic import validator
from typing import List

from cptk import Test
from cptk.utils import cached_property
from cptk.core import Configuration
from cptk.constants import (
    RECIPE_FILE,
    DEFAULT_TESTS_FOLDER,
    TEST_INPUT_FILE,
    TEST_OUTPUT_FILE,
)


class Recipe(Configuration):

    bake: List[str] = []
    serve: List[str]

    @validator('*', pre=True)
    @classmethod
    def string_to_commands(cls, val) -> List[str]:
        if isinstance(val, str):
            return val.split('\n')


@dataclass(unsafe_hash=True)
class LocalProblem:
    location: str = field(compare=True)

    @cached_property
    def recipe(self) -> Recipe:
        p = path.join(self.location, RECIPE_FILE)
        return Recipe.load(p)

    @cached_property
    def tests(self) -> List[Test]:
        base = path.join(self.location, DEFAULT_TESTS_FOLDER)

        l = list()
        inputs = glob(path.join(base, '*'), recursive=True)
        for inp in inputs:

            match = re.fullmatch(TEST_INPUT_FILE, inp)
            if not match:
                # If file doesn't match the TEST_INPUT_FILE regex, it is not
                # a valid test input file and it should be ignored.
                continue

            # Load input file
            with open(inp, 'r', encoding='utf8') as file:
                inp_data = file.read()

            # Generate the expected output file path for the current input
            out = match.expand(TEST_OUTPUT_FILE)

            try:
                with open(out, mode='r', encoding='utf8') as file:
                    out_data = file.read()
            except FileNotFoundError:
                out_data = None

            l.append(Test(inp_data, out_data))

        return l
