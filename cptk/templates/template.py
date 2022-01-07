import os
from dataclasses import dataclass


@dataclass
class Template:
    uid: str
    name: str
    path: str


HERE = os.path.dirname(__file__)

DEFAULT_TEMPLATES = (
    Template(
        uid='g++',
        name='C++ (Compiled with g++)',
        path=os.path.join(HERE, 'g++'),
    ),
    Template(
        uid='win-g++',
        name='C++ (Compiled with g++, Windows)',
        path=os.path.join(HERE, 'win-g++'),
    ),
    Template(
        uid='py',
        name='Python 3',
        path=os.path.join(HERE, 'py'),
    ),
    Template(
        uid='win-py',
        name='Python 3 (Windows)',
        path=os.path.join(HERE, 'win-py'),
    ),
)
