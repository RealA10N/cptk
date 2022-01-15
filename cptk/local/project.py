import os
from shutil import copytree, rmtree, copyfile
from dataclasses import dataclass, field

from pydantic import BaseModel

from cptk.core.preprocessor import Preprocessor
from cptk.local.problem import LocalProblem
from cptk.utils import cached_property, cptkException
from cptk.core import Configuration, System, Fetcher, DEFAULT_PREPROCESS
from cptk.templates import DEFAULT_TEMPLATES
from cptk.constants import (
    PROJECT_FILE,
    DEFAULT_TEMPLATE_FOLDER,
    DEFAULT_PREPROCESS as DEFAULT_PREPROCESS_DEST,
    DEFAULT_CLONE_PATH,
)


from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Type, TypeVar
    from cptk.scrape import Problem
    from cptk.templates import Template
    T = TypeVar('T')


class ProjectNotFound(cptkException):
    def __init__(self) -> None:
        super().__init__("Couldn't find a cptk project recursively")


class CloneSettings(BaseModel):
    path: str = DEFAULT_CLONE_PATH

    def dict(self, **kwargs) -> dict:
        kwargs.update({"exclude_unset": False})
        return super().dict(**kwargs)


class ProjectConfig(Configuration):
    template: str
    clone: CloneSettings

    git: Optional[bool] = False
    verbose: Optional[bool] = False
    preprocess: Optional[str] = None


@dataclass(unsafe_hash=True)
class LocalProject:
    location: str = field(compare=True)

    def __init__(self, location: str) -> None:
        self.location = location
        self.fetcher = Fetcher()

    @classmethod
    def is_project(cls, location: str) -> bool:
        """ Returns True if the given location is the root of a valid cptk
        project. """
        return os.path.isfile(os.path.join(location, PROJECT_FILE))

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

    @staticmethod
    def _copy_template(template: 'Template', dst: str) -> None:
        """ Copies the given template to the destination path. """

        if os.path.exists(dst):
            rmtree(dst)
        copytree(src=template.path, dst=dst)

    @staticmethod
    def _init_git(location: str) -> None:
        """ Initialized a new git repository in the given location. """

        # According to the git documentation (https://tinyurl.com/y3njm4n8):
        # "running 'git init' in an existing repository is safe", and thus,
        # we call it anyway!

        System.run(
            f'git init {location}',
            errormsg="Couldn't initialize git repository."
        )

    @classmethod
    def init(cls: 'Type[T]',
             location: str,
             template: str = None,
             git: bool = None,
             verbose: bool = None,
             ) -> 'T':
        """ Initialize an empty local project in the given location with the
        given properties and settings. Returns the newly created project as a
        LocalProject instance. """

        kwargs = dict()

        # Create the directory if it doesn't exist
        os.makedirs(location, exist_ok=True)

        if git is not None:
            kwargs['git'] = git
            if git:
                cls._init_git(location)

        if verbose is not None:
            kwargs['verbose'] = verbose

        if template is None:
            template = DEFAULT_TEMPLATE_FOLDER

        # Create default clone settings
        kwargs['clone'] = CloneSettings()

        # If the given template is actually one of the predefined template names
        temp_obj = {t.uid: t for t in DEFAULT_TEMPLATES}.get(template)
        if temp_obj is not None:
            dst = os.path.join(location, DEFAULT_TEMPLATE_FOLDER)
            cls._copy_template(temp_obj, dst)
            template = DEFAULT_TEMPLATE_FOLDER

        # Now 'template' actually has the path to the template folder.
        # Create the template folder if it doesn't exist yet
        os.makedirs(os.path.join(location, template), exist_ok=True)

        # Copy default preprocess into project
        copyfile(DEFAULT_PREPROCESS, os.path.join(
            location, DEFAULT_PREPROCESS_DEST))
        kwargs['preprocess'] = DEFAULT_PREPROCESS_DEST

        # Create the project configuration instance and dump it into a YAML
        # configuration file.
        config = ProjectConfig(template=template, **kwargs)
        config_path = os.path.join(location, PROJECT_FILE)
        config.dump(config_path)

        # We have created and initialized everything that is required for a
        # cptk project. Now we can create a LocalProject instance and return it.
        return cls(location)

    @cached_property
    def config(self) -> ProjectConfig:
        p = os.path.join(self.location, PROJECT_FILE)
        return ProjectConfig.load(p)

    def load_preprocess_globals(self, problem: 'Problem') -> dict:
        """ Executes the project's preprocessor and returns the avaliable
        globals dictionary. """

        globals = {'problem': problem}
        preprocess = self.relative(self.config.preprocess)

        if preprocess is not None:
            globals.update(Preprocessor.load_file(preprocess, globals))

        return globals

    def relative(self, path: str) -> str:
        """ If the given path is not absolute, returns the absolute path relative
        to the project location. """

        if path is not None and not os.path.isabs(path):
            path = os.path.join(self.location, path)
        return path

    def clone_url(self, url: str) -> LocalProblem:
        """ Clones the given URL as a probelm and stores as a local problem
        inside the current cptk project. """

        page = self.fetcher.to_page(url)
        problem = self.fetcher.page_to_problem(page)
        return self.clone_problem(problem)

    def clone_problem(self, problem: 'Problem') -> LocalProblem:
        """ Clones the given problem instance and stores a local problem inside
        the current cptk project. """

        globals = self.load_preprocess_globals(problem)

        src = self.relative(self.config.template)
        dst = self.relative(Preprocessor.parse_string(
            self.config.clone.path, globals))

        if os.path.isdir(dst):
            System.warn('Problem already exists locally')
            ans = System.ask(
                question="Are you sure you want to overwrite saved data? (y/n)",
                options={'y': True, 'n': False},
            )

            if not ans: System.abort()
            rmtree(dst)

        copytree(src, dst)
        Preprocessor.parse_directory(dst, globals)

        return LocalProblem.init(dst, problem)
