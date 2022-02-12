from os import getcwd

import cptk.utils
from cptk.core.collector import CommandCollector


collector = CommandCollector()

collector.global_argument(
    '-W', '--work-directory',
    dest='wd',
    metavar='PATH',
    default=getcwd(),
    type=cptk.utils.path_validator(
        dir_ok=True,
        file_ok=False,
        must_exist=True,
    )
)


@collector.command('init')
@collector.argument('template', type=str)
def init(wd: str, template: str):
    """ Initialize a new cptk project in the given location, using the provided
    project template. """

    from cptk.local.project import LocalProject
    from cptk.core.system import System

    LocalProject.init(
        location=wd,
        template=template,
        verbose=System.get_verbosity(),
    )


@collector.command('clone')
@collector.argument('url', type=cptk.utils.url_validator)
def clone(url: str):

    from cptk.local.project import LocalProject
    from cptk.core.system import System

    proj = LocalProject.find(getcwd())
    prob = proj.clone_url(url)
    proj.last = prob.location

    System.echo(prob.location)


@collector.command('last')
def last():
    """ Print the location of the last problem cptk interacted with. """

    from os import getcwd
    from cptk.local.project import LocalProject
    from cptk.core.system import System

    proj = LocalProject.find(getcwd())
    last = proj.last
    if last:
        System.echo(last)


@collector.command('move', aliases=['mv'])
@collector.argument(
    'src',
    type=cptk.utils.path_validator(dir_ok=True, file_ok=False, must_exist=True),
)
@collector.argument(
    'dst',
    type=cptk.utils.path_validator(dir_ok=True, file_ok=False, must_exist=True),
)
def move(src: str, dst: str):
    """ Moves a cloned problem to a new location. """

    from os import getcwd
    from cptk.local.project import LocalProject

    proj = LocalProject.find(getcwd())
    proj.move(src, dst)
