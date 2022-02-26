from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import pydantic

import cptk.constants
import cptk.scrape
import cptk.utils
from cptk.core.config import ConfigFileError
from cptk.core.config import ConfigFileNotFound
from cptk.core.config import Configuration
from cptk.core.system import System

if TYPE_CHECKING:
    from cptk.core.preprocessor import Preprocessor

T = TypeVar('T')


class RecipeNotFoundError(cptk.utils.cptkException):
    def __init__(self, filepath: str, msg: str) -> None:
        self.filepath = filepath
        super().__init__(msg)


class RecipeNameNotFound(RecipeNotFoundError):
    def __init__(self, filepath: str, name: str) -> None:
        self.name = name
        super().__init__(
            filepath,
            f'Recipe named {name!r} not found in recipes file {filepath!r}',
        )


class NoRecipesFound(RecipeNotFoundError):
    def __init__(self, filepath: str) -> None:
        super().__init__(
            filepath,
            f'No recipes found in recipes file {filepath!r}',
        )


class TestRecipe(pydantic.BaseModel):
    folder: str
    timeout: Union[float, str, None] = None

    def preprocess(self: T, processor: Preprocessor) -> type[T]:
        def parse_str(v):
            if isinstance(v, str):
                return processor.parse_string(v)
            else:
                return v

        kwargs = {
            'folder': parse_str(self.folder),
            'timeout': parse_str(self.timeout),
        }

        return type(self)(**kwargs)


class Recipe(pydantic.BaseModel):

    name: Optional[str] = None
    bake: List[str] = []
    serve: str
    test: Optional[TestRecipe] = None

    @pydantic.validator('bake', pre=True)
    @classmethod
    def string_to_commands(cls, val) -> List[str]:
        if isinstance(val, str):
            return val.split('\n')
        return val

    def preprocess(self: T, processor: Preprocessor) -> type[T]:
        def parse_str(v):
            if isinstance(v, str):
                return processor.parse_string(v)
            else:
                return v

        kwargs = {
            'name': parse_str(self.name),
            'bake': [parse_str(v) for v in self.bake],
            'serve': parse_str(self.serve),
            'test': self.test.preprocess(processor) if self.test else None,
        }

        return type(self)(**kwargs)


class RecipesConfig(Configuration):
    recipes: List[Recipe]


@dataclass(unsafe_hash=True)
class LocalProblem:
    location: str = field(compare=True)
    name: str | None = field(compare=True, default=None)

    @staticmethod
    def _store_test(folder: str, name: str, test: cptk.scrape.Test) -> None:

        inp = os.path.join(folder, name + cptk.constants.INPUT_FILE_SUFFIX)
        with open(inp, 'w', encoding='utf8') as file:
            file.write(test.input)

        out = os.path.join(folder, name + cptk.constants.OUTPUT_FILE_SUFFIX)
        if test.expected is not None:
            with open(out, 'w', encoding='utf8') as file:
                file.write(test.expected)

    def store_tests(self, folder: str, tests: list[cptk.scrape.Test]) -> None:
        if not tests:
            return
        gen = cptk.constants.TEST_NAME_GENERATOR()
        folder = os.path.join(self.location, folder)
        os.makedirs(folder, exist_ok=True)
        for test in tests:
            name = next(gen)
            self._store_test(folder, name, test)

    @classmethod
    def init(cls: type[T], location: str, recipe: Recipe) -> T:
        path = os.path.join(location, cptk.constants.RECIPE_FILE)
        config = None

        try:
            config = RecipesConfig.load(path)
        except ConfigFileNotFound:
            pass  # File doesn't exists -> we will create a new one later.
        except ConfigFileError:
            System.warn(
                f'Failed to parse existing recipe file {path!r}. '
                'Continuing the process will overwrite the file.',
            )
            ans = System.confirm('Are you sure you want to continue')
            if not ans:
                System.abort(0)

        if config is None:
            config = RecipesConfig(recipes=list())

        config.recipes.append(recipe)
        config.dump(path)

        return cls(location, recipe.name)

    @staticmethod
    def is_problem(location: str, name: str = None) -> bool:
        """ Returns True if the given directory contains a recipe with the given
        name. If a name isn't provided, returns True if a recipe file is located
        inside the given direcotry and it contains at least one recipe.  """

        path = os.path.join(location, cptk.constants.RECIPE_FILE)

        try:
            recipes = RecipesConfig.load(path)
        except ConfigFileError:
            return False

        names = {r.name for r in recipes.recipes}
        return len(names) > 0 if name is None else name in names

    @property
    def recipe(self) -> Recipe:
        path = os.path.join(self.location, cptk.constants.RECIPE_FILE)
        recipes = RecipesConfig.load(path).recipes

        if not recipes:
            raise NoRecipesFound(path)
        if self.name is None:
            return recipes[0]

        try:
            return next(r for r in recipes if r.name == self.name)
        except StopIteration:
            raise RecipeNameNotFound(path, self.name)
