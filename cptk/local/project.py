import os
from shutil import copytree, rmtree
from dataclasses import dataclass, field

from cptk.utils import cached_property
from cptk.core import Configuration, System
from cptk.templates import Template, DEFAULT_TEMPLATES
from cptk.constants import (
    PROJECT_FILE,
    DEFAULT_TEMPLATE_FOLDER,
)

from typing import Type, TypeVar, Optional
T = TypeVar('T')


class ProjectConfig(Configuration):
    template: str
    git: Optional[bool] = False
    verbose: Optional[bool] = False


@dataclass(unsafe_hash=True)
class LocalProject:
    location: str = field(compare=True)

    def __init__(self, location: str) -> None:
        self.location = location

    @classmethod
    def is_project(cls, location: str) -> bool:
        """ Returns True if the given location is the root of a valid cptk
        project. """
        return os.path.isfile(os.path.join(location, PROJECT_FILE))

    @classmethod
    def find(cls: Type[T], location: str) -> Optional[T]:
        """ Recursively searches if the given location is part of a cptk
        project, and if so, returns an instance of the project. """

        if cls.is_project(location):
            return cls(location)

        parent = os.path.dirname(location)
        return cls.find(parent) if parent != location else None

    @staticmethod
    def _copy_template(template: Template, dst: str) -> None:
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
    def init(cls: Type[T],
             location: str,
             template: str = None,
             git: bool = None,
             verbose: bool = None,
             ) -> T:
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

        # If the given template is actually one of the predefined template names
        temp_obj = {t.uid: t for t in DEFAULT_TEMPLATES}.get(template)
        if temp_obj is not None:
            dst = os.path.join(location, DEFAULT_TEMPLATE_FOLDER)
            cls._copy_template(temp_obj, dst)
            template = DEFAULT_TEMPLATE_FOLDER

        # Now 'template' actually has the path to the template folder.
        # Create the template folder if it doesn't exist yet
        os.makedirs(os.path.join(location, template), exist_ok=True)

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
