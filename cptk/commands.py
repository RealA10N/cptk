from os import getcwd

from cptk.core.collector import CommandCollector

collector = CommandCollector()


@collector.command('init')
@collector.argument('dir', type=str)
@collector.argument('template', type=str)
def init(dir: str, template: str):
    """ Initialize a new cptk project in the given location, using the provided
    project template. """

    from cptk.local.project import LocalProject
    from cptk.core.system import System

    LocalProject.init(
        location=dir,
        template=template,
        verbose=System.get_verbosity(),
    )


@collector.command('clone')
@collector.argument('url', type=str)
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
@collector.argument('dir', type=str)
@collector.argument('dst', type=str)
def move(dir: str, dst: str):
    """ Moves a cloned problem to a new location. """

    from os import getcwd
    from cptk.local.project import LocalProject

    proj = LocalProject.find(getcwd())
    proj.move(dir, dst)
