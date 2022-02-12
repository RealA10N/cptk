import os
import re
from dataclasses import dataclass
from dataclasses import field
from glob import glob
from typing import List
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import validator

from cptk.constants import DEFAULT_TESTS_FOLDER
from cptk.constants import RECIPE_FILE
from cptk.constants import TEST_INPUT_FILE_PATTERN
from cptk.constants import TEST_INPUT_FILE_STRUCTURE
from cptk.constants import TEST_OUTPUT_FILE_STRUCTURE
from cptk.constants import TEST_SAMPLE_NAME_STRUCTURE
from cptk.core.config import Configuration
from cptk.scrape import Test

if TYPE_CHECKING:
    from cptk.scrape.problem import Problem
    from typing import TypeVar, Type
    T = TypeVar("T")


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

    @staticmethod
    def is_problem(path: str) -> bool:
        """ Returns True if the given path represents a local problem. """
        return os.path.exists(os.path.join(path, RECIPE_FILE))

    @classmethod
    def init(cls: 'Type[T]', path: str, problem: 'Problem') -> 'T':
        cls._init_tests(
            path=os.path.join(path, DEFAULT_TESTS_FOLDER),
            tests=problem.tests,
        )

        return cls(os.path.abspath(path))

    @staticmethod
    def _init_tests(path: str, tests: List[Test]) -> None:
        for test, number in zip(tests, range(1, len(tests) + 1)):
            name = TEST_SAMPLE_NAME_STRUCTURE.format(num=number)

            inp = TEST_INPUT_FILE_STRUCTURE.format(name=name)
            inp_path = os.path.join(path, inp)

            out = TEST_OUTPUT_FILE_STRUCTURE.format(name=name)
            out_path = os.path.join(path, out)

            os.makedirs(path, exist_ok=True)

            with open(inp_path, 'w', encoding='utf8') as file:
                file.write(test.input)

            if test.expected is not None:
                with open(out_path, 'w', encoding='utf8') as file:
                    file.write(test.expected)

    @property
    def recipe(self) -> RecipeConfig:
        p = os.path.join(self.location, RECIPE_FILE)
        return RecipeConfig.load(p)

    @property
    def tests(self) -> List[Test]:
        base = os.path.join(self.location, DEFAULT_TESTS_FOLDER)

        res = list()
        inputs = glob(os.path.join(base, '*'), recursive=True)
        for inp in inputs:
            base, name = os.path.split(inp)

            match = re.fullmatch(re.compile(TEST_INPUT_FILE_PATTERN), name)
            if not match:
                # If file doesn't match the TEST_INPUT_FILE_PATTERN regex,
                # it is not a valid test input file and it should be ignored.
                continue

            # Load input file
            with open(inp, 'r', encoding='utf8') as file:
                inp_data = file.read()

            # Generate the expected output file path for the current input
            out_name = TEST_OUTPUT_FILE_STRUCTURE.format(**match.groupdict())
            out = os.path.join(base, out_name)

            try:
                with open(out, mode='r', encoding='utf8') as file:
                    out_data = file.read()
            except FileNotFoundError:
                out_data = None

            res.append(Test(inp_data, out_data))

        return res
