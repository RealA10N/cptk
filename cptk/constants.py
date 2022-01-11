RECIPE_FILE = '.cptk/recipe.cptk.yaml'
PROJECT_FILE = '.cptk/project.cptk.yaml'

DEFAULT_TEMPLATE_FOLDER = '.cptk/template'
DEFAULT_TESTS_FOLDER = '.cptk/tests'

TEST_INPUT_FILE_PATTERN = r'(P<name>.+)\.in'
TEST_OUTPUT_FILE_PATTERN = r'(P<name>.+)\.out'
TEST_INPUT_FILE_STRUCTURE = '{name}.in'
TEST_OUTPUT_FILE_STRUCTURE = '{name}.out'
TEST_SAMPLE_NAME_STRUCTURE = r'sample{num:03}'

PREPROCESSOR_PATTERN = r'\${{([^}]*)}}'
PREPROCESSOR_INVALID = '?'
DEFAULT_PREPROCESS = '.cptk/preprocess.py'

DEFAULT_CLONE_PATH = "${{ slugify(website) }}/${{ slugify(contest.name) }}/${{ slugify(problem.level) + '-' if problem.level is not None else '' }}${{ slugify(problem.name) }}"
