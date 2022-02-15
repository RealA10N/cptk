import os
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

from pydantic import BaseModel
from pydantic import validator

import cptk.constants
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
            f'Recipe named {name!r} not found in recipes file {filepath!r}'
        )


class NoRecipesFound(RecipeNotFoundError):
    def __init__(self, filepath: str) -> None:
        super().__init__(
            filepath,
            f'No recipes found in recipes file {filepath!r}'
        )


class Recipe(BaseModel):

    name: Optional[str] = None
    bake: List[str] = []
    serve: str

    @validator('bake', pre=True)
    @classmethod
    def string_to_commands(cls, val) -> List[str]:
        if isinstance(val, str):
            return val.split('\n')
        return val

    def preprocess(self: T, processor: 'Preprocessor') -> Type[T]:
        def parse_str(v):
            if isinstance(v, str): return processor.parse_string(v)
            else: return v

        kwargs = {
            'name': parse_str(self.name),
            'serve': parse_str(self.serve),
        }

        if self.bake: kwargs['bake'] = [parse_str(v) for v in self.bake]
        return type(self)(**kwargs)


class RecipesConfig(Configuration):
    recipes: List[Recipe]


@dataclass(unsafe_hash=True)
class LocalProblem:
    location: str = field(compare=True)
    name: Optional[str] = field(compare=True, default=None)

    @classmethod
    def init(cls: Type[T], location: str, recipe: Recipe) -> T:
        path = os.path.join(location, cptk.constants.RECIPE_FILE)
        config = None

        try:
            config = RecipesConfig.load(path)
        except ConfigFileNotFound:
            pass  # File doesn't exists -> we will create a new one later.
        except ConfigFileError:
            System.warn(f'Failed to parse existing recipe file {path!r}. '
                        'Continuing the process will overwrite the file.')
            ans = System.confirm('Are you sure you want to continue')
            if not ans: System.abort(0)

        if config is None: config = RecipesConfig(recipes=list())

        config.recipes.append(recipe)
        config.dump(path)

        return cls(location, recipe.name)

    @staticmethod
    def is_problem(location: str, name: str = None) -> bool:
        """ Returns True if the given directory contains a recipe with the given
        name. If a name isn't provided, returns True if a recipe file is located
        inside the given direcotry and it contains at least one recipe.  """

        path = os.path.join(location, cptk.constants.RECIPE_FILE)

        try: recipes = RecipesConfig.load(path)
        except ConfigFileError: return False

        names = {r.name for r in recipes.recipes}
        return len(names) > 0 if name is None else name in names

    @property
    def recipe(self) -> Recipe:
        path = os.path.join(self.location, cptk.constants.RECIPE_FILE)
        recipes = RecipesConfig.load(path).recipes

        if not recipes: raise NoRecipesFound(path)
        if self.name is None: return recipes[0]

        try: return next(r for r in recipes if r.name == self.name)
        except StopIteration: raise RecipeNameNotFound(path, self.name)
