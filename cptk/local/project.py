import os
from shutil import copytree, rmtree

from cptk.utils import cached_property
from cptk.core import Configuration
from cptk.templates import DEFAULT_TEMPLATES
from cptk.constants import (
    CPTK_FOLDER_NAME,
    PROJECT_CONFIG_NAME,
    DEFAULT_TEMPLATE_FOLDER,
)

from typing import Type, TypeVar
T = TypeVar('T')


class ProjectConfig(Configuration):
    template: str


class LocalProject:

    def __init__(self, location: str) -> None:
        self.location = location

    @classmethod
    def init(cls: Type[T], location: str, template: str = None) -> T:
        UID_TO_TEMPLATE = {
            template.uid: template
            for template in DEFAULT_TEMPLATES
        }

        if template is None:
            template = DEFAULT_TEMPLATE_FOLDER

        elif template in UID_TO_TEMPLATE:
            default_template = UID_TO_TEMPLATE[template]
            template = DEFAULT_TEMPLATE_FOLDER

            # copy default template to current project
            src = default_template.path
            dst = os.path.join(location, DEFAULT_TEMPLATE_FOLDER)
            if os.path.exists(dst):
                rmtree(dst)
            copytree(src, dst)

        config = ProjectConfig(template=template)

        cptk_folder = os.path.join(location, CPTK_FOLDER_NAME)
        os.makedirs(cptk_folder, exist_ok=True)

        config_path = os.path.join(cptk_folder, PROJECT_CONFIG_NAME)
        with open(config_path, 'w', encoding='utf8') as file:
            file.write(config.yaml())

        return cls(location)

    @cached_property
    def config(self) -> ProjectConfig:
        p = os.path.join(self.location, CPTK_FOLDER_NAME, PROJECT_CONFIG_NAME)
        return ProjectConfig.load(p)
