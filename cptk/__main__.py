import click
import sys
from os import getcwd
from functools import wraps

from cptk.utils import cptkException, valid_url
from cptk.templates import DEFAULT_TEMPLATES
from cptk.local import LocalProject
from cptk.core import System
from cptk.exceptions import SystemAbort, ProjectNotFound

from typing import Optional


def validate_url(_, __, value):
    if not valid_url(value):
        raise click.BadParameter(value)
    return value


@click.group()
@click.option(
    '-v/-q', '--verbose/--quiet', 'verbose',
    default=None,
    help='Print additional information.',
)
def cli(verbose: bool = None):
    if verbose is None:
        try:
            verbose = LocalProject.find(getcwd()).config.verbose
        except ProjectNotFound:
            pass

    System.set_verbosity(verbose)


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
@click.option(
    '--git/--no-git', is_flag=True, default=None,
    help='Initialize the project with a git repository.',
)
def init(location: str,
         template: Optional[str],
         git: Optional[bool],
         ) -> None:
    """ Initialize a new cptk project directory. """

    LocalProject.init(
        location=location,
        template=template,
        git=git,
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
    """ Show information about a specific problem or contest. """
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
    proj = LocalProject.find(getcwd())
    prob = proj.clone(url)
    click.echo(prob.location)


def main():
    """ The main function safely executes the click cli command group. If any
    errors are thrown, they will be converted into system messages and will be
    logged. """

    try:
        cli()

    except SystemAbort:  # pylint: disable=raise-missing-from
        raise click.Abort

    except cptkException as err:
        System.error(err)
        sys.exit(1)

    except Exception as err:  # pylint: disable=broad-except
        System.unexpected_error(err)
        sys.exit(2)

    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
