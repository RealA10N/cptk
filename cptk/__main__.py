import os
import sys
from typing import Optional

import click

from cptk.core import System
from cptk.exceptions import ProjectNotFound
from cptk.local import LocalProject
from cptk.templates import DEFAULT_TEMPLATES
from cptk.utils import cptkException
from cptk.utils import valid_url


class CatchAllExceptions(click.Group):

    EX_OK = 0
    EX_DATAERR = 65
    EX_SOFTWARE = 70

    def __call__(self, *args, **kwargs):
        """ The main function safely executes the click cli command group.
        If any errors are thrown, they will be converted into system messages
        and will be logged. """

        try:
            self.main(*args, **kwargs)

        # return code 1 is used when click aborts.

        except cptkException as err:
            System.error(err)
            sys.exit(self.EX_DATAERR)

        except Exception as err:
            System.unexpected_error(err)
            sys.exit(self.EX_SOFTWARE)

        else:
            sys.exit(self.EX_OK)


@click.group(cls=CatchAllExceptions)
@click.option(
    '-v/-q', '--verbose/--quiet', 'verbose',
    default=None,
    help='Print additional information.',
)
def cli(verbose: bool = None):
    if verbose is None:
        try:
            verbose = LocalProject.find(os.getcwd()).config.verbose
        except ProjectNotFound:
            pass

    System.set_verbosity(verbose)


def validate_url(_, __, value):
    if not valid_url(value):
        raise click.BadParameter(value)
    return value


@cli.command('init')
@click.argument(
    'location',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        writable=True, readable=True, resolve_path=True,
    ),
    required=False,
    default='.',
)
@click.option(
    '--template',
    type=click.Choice([
        temp.uid
        for temp in DEFAULT_TEMPLATES
    ]),
    help='Initialize the project with a predefined template matching the '
    'selected language and platfrom.',
)
def init(location: str, template: Optional[str]) -> None:
    """ Initialize a new cptk project directory. """

    LocalProject.init(
        location=location,
        template=template,
        verbose=System.get_verbosity(),
    )


@cli.command('show')
@click.argument(
    'url',
    type=str,
    callback=validate_url,
    required=True,
)
def show(url: str):
    """ Show information about a specific problem. """
    raise NotImplementedError  # TODO: implement cli show function


@cli.command('clone')
@click.argument(
    'url',
    type=str,
    callback=validate_url,
    required=True,
)
def clone(url: str):
    """ Clone a problem into a local cptk project. """
    proj = LocalProject.find(os.getcwd())
    prob = proj.clone_url(url)
    proj.last = prob.location
    click.echo(prob.location)


@cli.command('last')
def last():
    """ Print the location of the last problem cptk interacted with. """
    proj = LocalProject.find(os.getcwd())
    last = proj.last
    if last: click.echo(last)


@cli.command('move')
@click.argument(
    'src',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        writable=True, readable=True, resolve_path=True,
    ),
)
@click.argument(
    'dst',
    type=click.Path(
        file_okay=False, dir_okay=True,
        writable=True, readable=True, resolve_path=True,
    ),
)
def move(src: str, dst: str):
    """ Moves a cloned problem to a new location. """
    proj = LocalProject.find(os.getcwd())
    proj.move(src, dst)


def main():
    cli()


if __name__ == '__main__':
    main()
