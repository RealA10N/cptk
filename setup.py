from __future__ import annotations

from setuptools import find_packages
from setuptools import setup

import cptk

with open("README.md", encoding="utf8") as f:
    README = f.read()

with open("CHANGELOG.md", encoding="utf8") as f:
    CHANGELOG = f.read()

with open("requirements.txt", encoding="utf8") as f:
    DEPENDENCIES = f.read().splitlines()

setup(
    name="cptk",
    version=cptk.__version__,
    description=cptk.__description__,
    url='https://github.com/RealA10N/cptk',

    python_requires=">=3.7,<4",
    install_requires=DEPENDENCIES,

    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type="text/markdown",

    author=cptk.__author__,
    author_email=cptk.__author_email__,
    packages=find_packages(include=['cptk*']),
    include_package_data=True,

    entry_points={
        "cptk_sites": [
            "codeforces=cptk.websites:Codeforces",
            "csesfi=cptk.websites:Cses",
            "kattis=cptk.websites:Kattis",
        ],
        "console_scripts": [
            "cptk=cptk.main:main",
        ],
    },
)
