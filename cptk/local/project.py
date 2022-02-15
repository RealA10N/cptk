import os
import shutil
from dataclasses import dataclass
from dataclasses import field
from glob import iglob
from typing import List
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

from pydantic import BaseModel

import cptk.constants
import cptk.utils
from cptk.core.config import ConfigFileParsingError
from cptk.core.config import Configuration
from cptk.core.fetcher import Fetcher
from cptk.core.preprocessor import Preprocessor
from cptk.core.system import System
from cptk.core.templates import DEFAULT_TEMPLATES
from cptk.local.problem import LocalProblem
from cptk.local.problem import Recipe


if TYPE_CHECKING:
    from typing import Type, TypeVar
    from cptk.scrape import Problem
    from cptk.core.templates import Template
    T = TypeVar('T')


class ProjectNotFound(cptk.utils.cptkException):
    def __init__(self) -> None:
        super().__init__("Couldn't find a cptk project recursively")


class InvalidMovePath(cptk.utils.cptkException):
    def __init__(self, path: str, msg: str) -> None:
        self.path = path
        super().__init__(msg)


class InvalidMoveSource(InvalidMovePath):
    def __init__(self, path: str) -> None:
        super().__init__(path, f"Can't move {path!r}")


class InvalidMoveDest(InvalidMovePath):
    def __init__(self, path: str) -> None:
        super().__init__(path, f"Can't move to {path!r}")


class InvalidTemplate(cptk.utils.cptkException):
    pass


class CloneSettings(BaseModel):
    template: str
    path: str
    recipe: Recipe

    def dict(self, **kwargs) -> dict:
        kwargs.update({"exclude_unset": False})
        return super().dict(**kwargs)


class ProjectConfig(Configuration):
    clone: CloneSettings


@dataclass(unsafe_hash=True)
class LocalProject:
    location: str = field(compare=True)

    def __init__(self, location: str) -> None:
        self.location = location

    @cptk.utils.cached_property
    def fetcher(self) -> Fetcher:
        return Fetcher()

    @classmethod
    def is_project(cls, location: str) -> bool:
        """ Returns True if the given location is the root of a valid cptk
        project. """
        path = os.path.join(location, cptk.constants.PROJECT_FILE)
        return os.path.isfile(os.path.join(path))

    @classmethod
    def find(cls: 'Type[T]', location: str) -> 'T':
        """ Recursively searches if the given location is part of a cptk
        project, and if so, returns an instance of the project. If a project
        isn't found, an error is thrown. """

        if cls.is_project(location):
            return cls(location)

        parent = os.path.dirname(location)
        if parent == location:
            raise ProjectNotFound()

        return cls.find(parent)

    @classmethod
    def init(cls: 'Type[T]', location: str, template: str) -> 'T':
        """ Initialize an empty local project in the given location using the
        given template name. Returns the newly created project as a LocalProject
        instance. """

        avaliable_templates = {t.uid: t for t in DEFAULT_TEMPLATES}
        if template not in avaliable_templates:
            raise InvalidTemplate(f'Invalid template name {template!r}')

        template: 'Template' = avaliable_templates.get(template)
        commons = cptk.utils.find_common_files(location, template.path)

        if commons:
            System.warn('\n'.join((
                'The following files will be overwritten:',
                *commons,
            )))

            ans = System.confirm('Are you sure you want to continue')
            if not ans: System.abort()

        cptk.utils.soft_tree_copy(src=template.path, dst=location)
        return cls(location)

    @cptk.utils.cached_property
    def config(self) -> ProjectConfig:
        p = os.path.join(self.location, cptk.constants.PROJECT_FILE)
        return ProjectConfig.load(p)

    def _load_moves(self) -> List[Tuple[str, str]]:
        """ Loads information from the local moves file and returns the
        replacements directory. """

        moves_path = self.relative(cptk.constants.MOVE_FILE)

        try:
            with open(moves_path, 'r') as file:
                lines = file.read().splitlines(keepends=False)
        except FileNotFoundError:
            return list()

        moves = list()
        for lineno, line in enumerate(lines, start=1):
            parts = line.split(cptk.constants.MOVE_FILE_SEPERATOR)

            if len(parts) == 2:
                moves.append((parts[0], parts[1],))

            else:
                raise ConfigFileParsingError(
                    path=moves_path,
                    error=f'Seperator {cptk.constants.MOVE_FILE_SEPERATOR!r}'
                    ' not found',
                    position=(lineno, 0),
                )

        return moves

    @staticmethod
    def _is_subpath(parent: str, sub: str) -> bool:
        parent = os.path.abspath(parent)
        sub = os.path.abspath(sub)
        return os.path.commonpath([parent, sub]) == parent

    def _single_move(self, path: str, src: str, dst: str) -> str:
        """ If the given path shares a prefix with the move source, updates
        the path with by replacing the prefix with the destination prefix
        accordingly. If a prefix isn't shared, returns the original path
        without modifications. """

        if not self._is_subpath(src, path): return path
        rel = os.path.relpath(path, src)
        return os.path.normpath(os.path.join(dst, rel))

    def move_relative(self, path: str) -> str:
        """ Applies all registered move transformations to the given path, and
        returns the new path, as an abs path. """

        path = self.relative(path)
        for src, dst in self._load_moves():
            path = self._single_move(
                path,
                self.relative(src),
                self.relative(dst),
            )
        return path

    def relative(self, path: str) -> str:
        """ If the given path is not absolute, returns the absolute path relative
        to the project location. """

        if path is not None and not os.path.isabs(path):
            path = os.path.join(self.location, path)
        return path

    def clone_url(self, url: str) -> LocalProblem:
        """ Clones the given URL as a problem and stores as a local problem
        inside the current cptk project. """

        page = self.fetcher.to_page(url)
        problem = self.fetcher.page_to_problem(page)
        return self.clone_problem(problem)

    def clone_problem(self, problem: 'Problem') -> LocalProblem:
        """ Clones the given problem instance and stores a local problem inside
        the current cptk project. """

        processor = Preprocessor(problem)

        src = self.relative(self.config.clone.template)
        dst = self.move_relative(processor.parse_string(self.config.clone.path))
        commons = cptk.utils.find_common_files(src, dst)

        if commons:
            System.warn('\n'.join((
                'The following files will be overwritten:',
                *commons,
            )))

            ans = System.confirm('Are you sure you want to continue')
            if not ans: System.abort()

        cptk.utils.soft_tree_copy(src, dst)
        recipe = self.config.clone.recipe.preprocess(processor)
        prob = LocalProblem.init(dst, recipe)

        processor.parse_directory(dst)
        self.update_last(prob)
        return prob

    def last(self) -> Optional[LocalProblem]:
        try:
            with open(self.relative(cptk.constants.LAST_FILE), 'r') as file:
                data = file.read()
        except FileNotFoundError:
            return None

        location, _, name = data.partition(cptk.constants.LAST_FILE_SEPERATOR)
        return LocalProblem(location, name if name else None)

    def update_last(self, prob: LocalProblem) -> None:
        path = self.relative(cptk.constants.LAST_FILE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            location = prob.location
            name = str() if prob.name is None else prob.name
            file.write(f'{location}{cptk.constants.LAST_FILE_SEPERATOR}{name}')

    def move(self, src: str, dst: str) -> None:
        """ Validates that the given source and destination directories are
        can be moved, and if so, moves source to destination and record the
        move. After the move, new problem that share a prefix with the source
        will be created in the given destination with the matching suffix. """

        # normalize paths to their unique absolute representation
        src = os.path.normpath(self.relative(src))
        dst = os.path.normpath(self.relative(dst))

        if not self._is_subpath(self.location, src) or not os.path.isdir(src):
            raise InvalidMoveSource(src)

        if not self._is_subpath(self.location, dst):
            raise InvalidMoveDest(dst)

        for pat in cptk.constants.MOVE_SAFES:
            # This is an ugly solution. I have tries to use fnmatch but
            # it has some strange behavior and doesn't match directories
            # if their name doesn't end with an '/'. I should rewrite this
            # piece of code, but as long as it works and preforms ok-ish,
            # I'm fine with it. (:

            matches = (
                os.path.normpath(g)
                for g in iglob(self.relative(pat), recursive=True)
            )
            if os.path.normpath(src) in matches:
                raise InvalidMoveSource(src)

        shutil.move(src, dst)
        self._register_move(src, dst)

    def _register_move(self, src: str, dst: str) -> None:
        """ Registers the given (src, dst) pair as a project move. It is then
        used by the 'move_relative' method to parse and generate the moved
        paths. """

        src = os.path.relpath(src, self.location)
        dst = os.path.relpath(dst, self.location)

        with open(self.relative(cptk.constants.MOVE_FILE), 'a') as file:
            file.write(f'{src}{cptk.constants.MOVE_FILE_SEPERATOR}{dst}\n')
