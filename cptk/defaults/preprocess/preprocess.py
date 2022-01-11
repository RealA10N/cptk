# This file contains executable python code.
# This file will before cloning new problems, and the globals avaliable at
# the end of the execution will be avaliable to use in your problem template
# as strings. If, for example, we define here a variable named 'hello' with
# the string value "There", if you use ${{ hello }} in your template files or
# even in your subdirectory or file names, it will be replaced with "There".
# Note that the string inside the ${{}} is actually python code too, so
# using ${{ hello.upper() }} for example will yield "THERE".
# If an __all__ list is provided, only globals from the list will be avaliable
# to use in the templates.

from os import getlogin
from datetime import datetime
from slugify import slugify

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cptk.scrape import Problem

    here: str = None
    problem: 'Problem' = None

# Unpack important problem attributes
contest = problem.contest
website = problem.website.name()
domain = problem.website.domain()

# Calculate constants
ctime = datetime.now().ctime()
user = getlogin()

__all__ = ['problem', 'contest', 'website',
           'domain', 'ctime', 'user', 'slugify']
