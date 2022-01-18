RECIPE_FILE = '.cptk/recipe.cptk.yaml'
PROJECT_FILE = '.cptk/project.cptk.yaml'

DEFAULT_TEMPLATE_FOLDER = '.cptk/template'
DEFAULT_TESTS_FOLDER = '.cptk/tests'

TEST_INPUT_FILE_PATTERN = r'in(?P<name>.+)\.txt'
TEST_OUTPUT_FILE_PATTERN = r'out(?P<name>.+)\.txt'
TEST_INPUT_FILE_STRUCTURE = 'in{name}.txt'
TEST_OUTPUT_FILE_STRUCTURE = 'out{name}.txt'
TEST_SAMPLE_NAME_STRUCTURE = r'{num:02}'

PREPROCESSOR_PATTERN = r'\${{([^}]*)}}'
PREPROCESSOR_INVALID = '?'
DEFAULT_PREPROCESS = '.cptk/preprocess.py'

DEFAULT_CLONE_PATH = '/'.join((
    '${{ slugify(website.name) }}',
    '${{ slugify(contest.name) }}',
    '${{ slugify(problem.name) }}',
))
