class cptkException(Exception):
    """ Base cptk exception. All exceptions raised and created by cptk should
    inherent from this one. """

# fmt: off

# Those imports should be placed below cptkException to avoid circular import
# errors

from cptk.core.integrator import InvalidClone, UnknownWebsite

# fmt: on

__all__ = [
    'cptkException',
    'InvalidClone',
    'UnknownWebsite',
]
