from os import getcwd

import cptk.utils
from cptk.core.collector import CommandCollector
from cptk.core.system import System


collector = CommandCollector()

collector.global_argument(
    '-W', '--work-directory',
    help='set the working directory (defaults to cwd)',
    dest='wd',
    metavar='DIRECTORY',
    default=getcwd(),
    type=cptk.utils.path_validator(
        dir_ok=True,
        file_ok=False,
        must_exist=True,
    )
)

collector.global_argument(
    '-v',
    action='count',
    dest='_verbosity',
    help='increase the verbosity of the program',
)


collector.global_argument(
    '-y', '--yes',
    action='count',
    default=0,
    dest='_yes_count',
    help="don't ask for confirmation, assume that it is provided",
)


@collector.preprocessor
def preprocessor(namespace):
    System.set_verbosity(namespace._verbosity)
    System.set_yes(namespace._yes_count)
    return namespace


@collector.command(
    'initialize',
    aliases=['init'],
    help='initialize a new cptk project',
    description='Initialize a new cptk project in the given location, '
                'using the provided project template.',
)
@collector.argument('template', type=str)
def initialize(wd: str, template: str, verbosity: int = None):
    """ Initialize a new cptk project in the given location, using the provided
    project template. """

    from cptk.local.project import LocalProject

    LocalProject.init(
        location=wd,
        template=template,
        verbosity=verbosity,
    )


@collector.command(
    'clone',
    help='clones a problem into a local cptk project',
    description='Clones a problem from a supported website into a local cptk '
                'project. ',
)
@collector.argument(
    'url',
    help='the problem to be cloned',
    type=cptk.utils.url_validator
)
def clone(url: str, wd: str):

    from cptk.local.project import LocalProject
    from cptk.core.system import System

    proj = LocalProject.find(wd)
    prob = proj.clone_url(url)
    proj.last = prob.location

    System.echo(prob.location)


@collector.command(
    'last',
    help='outputs the last problem touched by cptk',
    description='Outputs the absolute location of that last problem that the '
                'cptk CLI interacted with.',
)
def last(wd: str):
    """ Print the location of the last problem cptk interacted with. """

    from cptk.local.project import LocalProject
    from cptk.core.system import System

    proj = LocalProject.find(wd)
    last = proj.last
    if last:
        System.echo(last)


@collector.command(
    'move',
    aliases=['mv'],
    help='moves a cloned problem to a new location',
    description='Moves a cloned problem to a new location.',
)
@collector.argument(
    'src',
    type=cptk.utils.path_validator(dir_ok=True, file_ok=False, must_exist=True),
)
@collector.argument(
    'dst',
    type=cptk.utils.path_validator(dir_ok=True, file_ok=False, must_exist=True),
)
def move(src: str, dst: str, wd: str):
    """ Moves a cloned problem to a new location. """

    from cptk.local.project import LocalProject

    proj = LocalProject.find(wd)
    proj.move(src, dst)
