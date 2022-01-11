import click
import sys
from os import getcwd
from functools import wraps

from cptk.utils import cptkException, valid_url
from cptk.templates import DEFAULT_TEMPLATES
from cptk.local import LocalProject
from cptk.core import System

from typing import Optional


def print_exceptions(f):
    """ A decorator that safely runs the function it wraps.
    If the function throws any errors, they will be converted into system
    messages and will be logged. """

    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            f(*args, **kwargs)

        except cptkException as err:
            System.error(err)
            sys.exit(1)

        except Exception as err:
            System.unexpected_error(err)
            sys.exit(2)

        else:
            sys.exit(0)

    return decorator


def validate_url(_, __, value):
    if not valid_url(value):
        raise click.BadParameter(value)
    return value


@click.group()
@click.option(
    '-v/-q', '--verbose/--quite', 'verbose',
    default=None,
    help='Print additional information.',
)
def cli(verbose: bool = None):
    if verbose is None:
        proj = LocalProject.find(getcwd())
        if proj is not None:
            verbose = proj.config.verbose

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
@print_exceptions
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
@print_exceptions
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
@print_exceptions
def clone(url: str):
    """ Clone a problem into a local cptk project. """
    raise NotImplementedError  # TODO: implement cli clone function


if __name__ == '__main__':
    cli()
