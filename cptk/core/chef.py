from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cptk.local import LocalProject
    from cptk.local import LocalProblem


class Chef:
    """ Bake, serve and test local problems. """

    def __init__(
        self,
        project: 'LocalProject',
        problem: 'LocalProblem',
    ) -> None:
        self._project = project
        self._problem = problem

    def baked(self) -> bool:
        """ Checks if the problem executable is up to date, and returns True if
        it is. If the problem solution configuration doesn't specify a bake
        recipe, returns True. """

    def bake(self) -> None:
        """ Bakes (generates) the executable of the current problem solution.
        If the recipe configuration file of the current problem doesn't specify
        a 'bake' option, returns None quietly. """

    def serve(self) -> None:
        """ Bakes the local problem (if a baking recipe is provided), and serves
        it while piping the standard input to the executable. """

    def test(self) -> None:
        """ Bakes (if a baking recipe is provided) and serves the local tests
        that are linked to the problem. """
