import argparse
import inspect
from collections import defaultdict
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar

F = TypeVar('F')


class CommandCollector:

    def __init__(self, *args, **kwargs) -> None:
        self._parser = argparse.ArgumentParser(*args, **kwargs)
        self._subparsers = self._parser.add_subparsers()
        self._args: Dict[Callable, List[Tuple]] = defaultdict(list)

        self._preprocessor = lambda v: v

        # Print the default help message if no command is provided
        self._parser.set_defaults(func=self._parser.print_help)

    def global_argument(self, *args, **kwargs) -> None:
        return self._parser.add_argument(*args, **kwargs)

    def argument(self, *args, **kwargs) -> Callable[[F], F]:
        """ Returns a decorator that adds an argument to a command function.
        A wrapper around the argparse.add_argument function. """

        # We want to support decorator stacking where the top decorator is
        # the command decorator, and the decorators after that are the argument
        # decorators, in order from top to bottom. Python executes the
        # decorators in the opposite order (from the bottom to top), and thus
        # we store all the argument decorations until we see a command decorator

        def decorator(func: F) -> F:
            self._args[func].append((args, kwargs))
            return func

        return decorator

    def command(self, *args, **kwargs) -> Callable[[F], F]:
        """ Returns a decorator that creates a new subcommand parser.
        A wrapper around the add_subparsers and add_parser functions. """

        # The command decorator should be the top decorator, which means that he
        # is the last one to be executed. All the arguments are already stored
        # in the '_args' dictionary, and that is left to do is to add them to
        # the parser in the revere order.

        def decorator(func: F) -> F:
            parser = self._subparsers.add_parser(*args, **kwargs)
            for a, k in reversed(self._args[func]):
                parser.add_argument(*a, **k)

            parser.set_defaults(func=func)
            return func

        return decorator

    def preprocessor(
        self,
        func: Callable[[argparse.Namespace], argparse.Namespace],
    ) -> Callable[[argparse.Namespace], argparse.Namespace]:
        self._preprocessor = func
        return func

    def run(self, args: List[str] = None):
        """ Executes the appropriate subcommand using the given arguments. """

        args = self._parser.parse_args(args)
        args = self._preprocessor(args)
        args: dict = vars(args)

        func: Callable = args.pop('func')
        sig = inspect.signature(func)

        return func(**{
            key: value for key, value in args.items()
            if key in sig.parameters.keys()
        })
