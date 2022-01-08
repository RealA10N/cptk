import os
from shutil import copytree, rmtree

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


class LocalProject:

    def __init__(self, location: str) -> None:
        self.location = location

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
             git: bool = False,
             ) -> T:
        """ Initialize an empty local project in the given location with the
        given properties and settings. Returns the newly created project as a
        LocalProject instance. """

        kwargs = dict()

        # Create the directory if it doesn't exist
        os.makedirs(location, exist_ok=True)
        if git:
            cls._init_git(location)
            kwargs['git'] = True

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
        os.makedirs(template, exist_ok=True)

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
