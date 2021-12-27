from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf8") as f:
    README = f.read()

with open("requirements.txt", mode="r", encoding="utf8") as f:
    DEPENDENCIES = f.read().splitlines()

setup(
    name="cptk",
    version="0.1.0",
    description="Your personal assistant for everything competitive programming related!",
    python_requires=">=3.6,<4",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Alon Krymgand Osovsky",
    author_email="downtown2u@gmail.com",
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    entry_points={
        "cptk_sites": [
            "codeforces=cptk.websites:Codeforces",
            "csesfi=cptk.websites:CsesFi",
        ],
        "console_scripts": [
            "cptk=cptk.__main__:cli",
        ]
    },
)
