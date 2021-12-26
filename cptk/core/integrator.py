import pkg_resources

from cptk.exceptions import InvalidClone

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from cptk import Website, PageInfo, Contest, Problem


class Integrator:

    def __init__(self) -> None:
        self._websites = self._load_websites()

    def _load_websites(self) -> List['Website']:
        return [
            point.load()
            for point in pkg_resources.iter_entry_points('cptk_sites')
        ]

    # --------------------------------------------------------------- Clone -- #

    def clone_webpage(self, info: 'PageInfo') -> None:
        """ Recives an arbitrary page info instance and tries to match it with
        a Website class that knows how to handle this specific website. If cptk
        doesn't find a way to parse the given webpage, it raises the
        'InvalidClone' exception. """

        for w in self._websites:
            if w.is_problem(info):
                return self.clone_problem(w.to_problem(info))
            elif w.is_contest(info):
                return self.clone_contest(w.to_contest(info))
        raise InvalidClone(info)

    def clone_contest(self, contest: 'Contest') -> None:
        """ Clones the given contest and every problem in to. """
        raise NotImplementedError  # TODO implement clone_contest method

    def clone_problem(self, problem: 'Problem') -> None:
        """ Clones the given problem. """
        raise NotImplementedError  # TODO implement clone_problem method
