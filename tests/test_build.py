import subprocess
import sys


def test_same_version():
    """ Test the the version in setup.py matches the version in __init__.py """

    res = subprocess.run(
        [sys.executable, '-m', 'pip', 'show', 'cptk'],
        stdout=subprocess.PIPE,
        check=True,
        encoding='utf8'
    )

    fields = {
        line.partition(':')[0]: line.partition(':')[-1].strip()
        for line in res.stdout.split('\n')
    }

    from cptk import __version__
    assert __version__ == fields['Version']
