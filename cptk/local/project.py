from os import path

from pydantic import BaseModel, validator

from cptk.utils import cached_property
from cptk.templates import DEFAULT_TEMPLATES
from cptk.constants import CPTK_FOLDER_NAME, PROJECT_CONFIG_NAME
from cptk.core import load_config_file


class Home(BaseModel):
    template: str

    @validator('template')
    @classmethod
    def validate_template(cls, value: str) -> str:
        """ Template can either a uid of one of the pre-defined templates
        avaliable simply by installing cptk, or a path to a folder containing
        a recipe configuration file. """

        uid_to_template = {
            template.uid: template
            for template in DEFAULT_TEMPLATES
        }

        if value in uid_to_template:
            return uid_to_template[value].path

        return value


class LocalProject:

    def __init__(self, location: str) -> None:
        self.location = location

    @cached_property
    def home(self) -> Home:
        p = path.join(self.location, CPTK_FOLDER_NAME, PROJECT_CONFIG_NAME)
        return load_config_file(p, Home)
