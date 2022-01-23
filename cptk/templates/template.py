import os
from dataclasses import dataclass


@dataclass
class Template:
    uid: str
    name: str
    path: str


HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, '..')
TEMPLATES_FOLDER = os.path.normpath(os.path.join(SRC, 'defaults', 'templates'))

DEFAULT_TEMPLATES = (
    Template(
        uid='g++',
        name='C++ (Compiled with g++)',
        path=os.path.join(TEMPLATES_FOLDER, 'g++'),
    ),
    Template(
        uid='py',
        name='Python 3',
        path=os.path.join(TEMPLATES_FOLDER, 'py'),
    ),
)
