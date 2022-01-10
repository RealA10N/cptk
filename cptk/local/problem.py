import re
from os import path
from glob import glob
from dataclasses import dataclass, field

from pydantic import BaseModel, validator

from cptk.scrape import Test
from cptk.utils import cached_property
from cptk.core import Configuration
from cptk.constants import (
    RECIPE_FILE,
    DEFAULT_TESTS_FOLDER,
    TEST_INPUT_FILE_PATTERN,
    TEST_INPUT_FILE_STRUCTURE,
    TEST_OUTPUT_FILE_STRUCTURE,
    TEST_SAMPLE_NAME_STRUCTURE,
)

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from cptk.scrape import Problem


class Recipe(BaseModel):

    bake: List[str] = []
    serve: List[str]

    @validator('*', pre=True)
    @classmethod
    def string_to_commands(cls, val) -> List[str]:
        if isinstance(val, str):
            return val.split('\n')


class RecipeConfig(Configuration):
    solution: Recipe


@dataclass(unsafe_hash=True)
class LocalProblem:
    location: str = field(compare=True)

    def _dump_tests(self, tests: List[Test]) -> None:

        base = path.join(self.location, DEFAULT_TESTS_FOLDER)

        for test, number in tests, range(1, len(tests) + 1):
            name = TEST_SAMPLE_NAME_STRUCTURE.format(num=number)

            inp = TEST_INPUT_FILE_STRUCTURE.format(name=name)
            inp_path = path.join(base, inp)

            out = TEST_OUTPUT_FILE_STRUCTURE.format(name=name)
            out_path = path.join(base, out)

            with open(inp_path, 'w', encoding='utf8') as file:
                file.write(test.input)

            with open(out_path, 'w', encoding='utf8') as file:
                file.write(test.expected)

    def dump(self, problem: 'Problem') -> None:
        """ Recives problem information and dumps it in the local location.
        This includes dumping the example test cases. """

        self._dump_tests(problem.tests)

    @cached_property
    def recipe(self) -> RecipeConfig:
        p = path.join(self.location, RECIPE_FILE)
        return RecipeConfig.load(p)

    @cached_property
    def tests(self) -> List[Test]:
        base = path.join(self.location, DEFAULT_TESTS_FOLDER)

        l = list()
        inputs = glob(path.join(base, '*'), recursive=True)
        for inp in inputs:

            match = re.fullmatch(TEST_INPUT_FILE_PATTERN, inp)
            if not match:
                # If file doesn't match the TEST_INPUT_FILE_PATTERN regex,
                # it is not a valid test input file and it should be ignored.
                continue

            # Load input file
            with open(inp, 'r', encoding='utf8') as file:
                inp_data = file.read()

            # Generate the expected output file path for the current input
            out = TEST_OUTPUT_FILE_STRUCTURE.format(**match.groupdict())

            try:
                with open(out, mode='r', encoding='utf8') as file:
                    out_data = file.read()
            except FileNotFoundError:
                out_data = None

            l.append(Test(inp_data, out_data))

        return l
