import os
import subprocess
import sys
from dataclasses import dataclass
from threading import Timer
from typing import Optional
from typing import TypeVar

import cptk.utils
from cptk.core.system import System
from cptk.local.problem import LocalProblem

T = TypeVar('T')


@dataclass
class RunnerResult:
    runner: 'Runner'
    code: int
    timed_out: bool
    outs: Optional[str] = None
    errs: Optional[str] = None


class Nothing:
    def __getattribute__(self: T, *_) -> T:
        return self

    def __call__(self: T, *_, **__) -> T:
        return self


class BakingError(cptk.utils.cptkException):
    def __init__(self, code: int, cmd: str) -> None:
        self.code = code
        self.cmd = cmd
        super().__init__(
            f'Execution of command resulted in exit code {code}:\n{cmd}'
        )


class Runner:
    def __init__(self, env: dict = None) -> None:
        self.env = env if env is not None else os.environ

    def exec(
        self,
        cmd: str,
        input: str = None,
        timeout: float = None,
        redirect: bool = True,
        wd: str = None,
    ) -> RunnerResult:
        """ Executes the given command, and returns a 'RunnerResult' instance
        that describes the result of the execution.
        If input is provided, it is piped into the input of the subprocess.
        If timeout is provided, the execution of the process will get
        terminated after the provided amount of seconds. """

        proc = subprocess.Popen(
            cmd.split(),
            cwd=wd,
            env=self.env,
            encoding='utf8',
            stdin=subprocess.PIPE if redirect else sys.stdin,
            stdout=subprocess.PIPE if redirect else sys.stdout,
            stderr=subprocess.PIPE if redirect else sys.stderr,
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
            outs=proc.stdout.read() if redirect else None,
            errs=proc.stderr.read() if redirect else None,
            code=proc.returncode,
            timed_out=timed_out,
        )


class Chef:
    """ Bake, serve and test local problems. """

    def __init__(self, problem: LocalProblem) -> None:
        self._problem = problem
        self._runner = Runner()

    def bake(self) -> None:
        """ Bakes (generates) the executable of the current problem solution.
        If the recipe configuration file of the current problem doesn't specify
        a 'bake' option, returns None quietly. """

        location = self._problem.location

        for cmd in self._problem.recipe.bake:
            System.log(cmd)
            res = self._runner.exec(cmd, wd=location, redirect=False)
            if res.code: raise BakingError(res.code, cmd)

    def serve(self) -> None:
        """ Bakes the local problem (if a baking recipe is provided), and serves
        it while piping the standard input to the executable. """

        self.bake()

        cmd = self._problem.recipe.serve
        location = self._problem.location

        System.log(cmd)
        res = self._runner.exec(cmd, wd=location, redirect=False)
        System.abort(res.code)

    def test(self) -> None:
        """ Bakes (if a baking recipe is provided) and serves the local tests
        that are linked to the problem. """
