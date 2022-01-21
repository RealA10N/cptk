from setuptools import find_packages
from setuptools import setup

with open("README.md", mode="r", encoding="utf8") as f:
    README = f.read()

with open("requirements.txt", mode="r", encoding="utf8") as f:
    DEPENDENCIES = f.read().splitlines()

DESC = "Your personal assistant for everything competitive-programming-related"

setup(
    name="cptk",
    version="0.1.0",
    description=DESC,

    python_requires=">=3.6,<4",
    install_requires=DEPENDENCIES,

    long_description=README,
    long_description_content_type="text/markdown",

    author="Alon Krymgand Osovsky",
    author_email="downtown2u@gmail.com",

    packages=find_packages(include=['cptk*']),
    package_dir={'cptk': 'cptk'},
    package_data={'cptk': ['defaults/*']},

    entry_points={
        "cptk_sites": [
            "codeforces=cptk.websites:Codeforces",
            "csesfi=cptk.websites:Cses",
            "kattis=cptk.websites:Kattis",
        ],
        "console_scripts": [
            "cptk=cptk.__main__:main",
        ]
    },
)
