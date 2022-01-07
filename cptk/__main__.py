import click

from cptk.utils import valid_url
from cptk.templates import DEFAULT_TEMPLATES
from cptk.local import LocalProject


@click.group()
def cli():
    pass


def validate_url(_, __, value):
    if not valid_url(value):
        raise click.BadParameter(value)
    return value


@cli.command('init')
@click.argument(
    'location',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True,
        writable=True, readable=True, resolve_path=True),
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
    '--git', is_flag=True,
    help='Initialize the project with a git repository.',
)
def init(location: str,
         template: str,
         git: bool,
         ) -> None:
    """ Initialize a new cptk project directory. """

    LocalProject.init(location=location, template=template, git=git)


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
    raise NotImplementedError  # TODO: implement cli clone function


if __name__ == '__main__':
    cli()
