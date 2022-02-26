from __future__ import annotations

RECIPE_FILE = 'recipes.cptk.yaml'
PROJECT_FILE = '.cptk/project.cptk.yaml'
LAST_FILE = '.cptk/stayaway/last.cptk.txt'

MOVE_FILE = '.cptk/moves.cptk.txt'
MOVE_FILE_SEPERATOR = '::'
MOVE_SAFES = ['./', '**/.cptk/**']

LAST_FILE_SEPERATOR = '::'

INPUT_FILE_SUFFIX = '.in'
OUTPUT_FILE_SUFFIX = '.out'


def TEST_NAME_GENERATOR():
    n = 1
    while True:
        yield f'sample{n:02d}'
        n += 1
