import click


@click.group()
def cli():
    pass


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
    """ Initializes a new cptk project directory. """
    raise NotImplementedError


if __name__ == '__main__':
    cli()
