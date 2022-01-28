from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cptk.local import LocalProblem
    from typing import TypeVar
    T = TypeVar('T')


import os
import shlex
import subprocess
from threading import Timer
from dataclasses import dataclass


@dataclass
class RunnerResult:
    runner: 'Runner'
    outs: str
    errs: str
    code: int
    timed_out: bool


class Nothing:
    def __getattribute__(self: 'T', *_) -> 'T':
        return self

    def __call__(self: 'T', *_, **__) -> 'T':
        return self


class Runner:
    def __init__(self, env: dict = None) -> None:
        self.env = env if env is not None else os.environ

    def exec(
        self,
        cmd: str,
        input: str = None,
        timeout: float = None,
    ) -> RunnerResult:
        """ Executes the given command, and returns a 'RunnerResult' instance
        that describes the result of the execution.
        If input is provided, it is piped into the input of the subprocess.
        If timeout is provided, the execution of the process will get
        terminated after the provided amount of seconds. """

        proc = subprocess.Popen(
            shlex.split(cmd),
            env=self.env,
            encoding='utf8',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # I used a timer thread and a Popen instance instead of the builtin
        # run or communicate methods with the 'timeout' argument to allow
        # capturing the stdin and stderr even if we terminate the process.

        timer = Timer(timeout, proc.kill) if timeout is not None else Nothing()

        if input is not None:
            proc.stdin.write(input)
            proc.stdin.flush()

        try:
            timer.start()
            proc.wait()
        finally:
            timed_out = False if timeout is None else not timer.is_alive()
            timer.cancel()

        return RunnerResult(
            runner=self,
            outs=proc.stdout.read(),
            errs=proc.stderr.read(),
            code=proc.returncode,
            timed_out=timed_out,
        )


class Chef:
    """ Bake, serve and test local problems. """

    def __init__(self, problem: 'LocalProblem') -> None:
        self._problem = problem

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
