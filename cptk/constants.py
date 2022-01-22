RECIPE_FILE = '.cptk/recipe.cptk.yaml'
PROJECT_FILE = '.cptk/project.cptk.yaml'
LAST_FILE = '.cptk/stayaway/last.cptk.txt'

MOVE_FILE = '.cptk/moves.cptk.txt'
MOVE_FILE_SEPERATOR = '::'
MOVE_SAFES = ['./', '**/.cptk/**']

DEFAULT_TEMPLATE_FOLDER = '.cptk/template'
DEFAULT_TESTS_FOLDER = '.cptk/tests'

TEST_INPUT_FILE_PATTERN = r'in(?P<name>.+)\.txt'
TEST_OUTPUT_FILE_PATTERN = r'out(?P<name>.+)\.txt'
TEST_INPUT_FILE_STRUCTURE = 'in{name}.txt'
TEST_OUTPUT_FILE_STRUCTURE = 'out{name}.txt'
TEST_SAMPLE_NAME_STRUCTURE = r'{num:02}'

DEFAULT_PREPROCESS = '.cptk/preprocess.py'

DEFAULT_CLONE_PATH = '/'.join((
    '{{ problem.website.name | slug }}',
    '{% if problem.contest is defined %}'
    '{% if problem.contest.name is defined %}'
    '{{ problem.contest.name | slug }}'
    '{% endif %}{% endif %}',
    '{{ problem.name | slug }}',
))
