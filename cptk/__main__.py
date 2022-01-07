import click

from cptk.utils import valid_url


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
def init(location: str):
    """ Initialize a new cptk project directory. """
    raise NotImplementedError  # TODO: implement cli init function


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
