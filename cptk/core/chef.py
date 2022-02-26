from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from threading import Timer
from typing import TypeVar

import cptk.constants
import cptk.utils
from cptk.core.system import System
from cptk.local.problem import LocalProblem
from cptk.scrape import Test

T = TypeVar('T')


@dataclass
class RunnerResult:
    runner: Runner
    code: int
    timed_out: bool
    outs: str | None = None
    errs: str | None = None


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
            f'Execution of command resulted in exit code {code}:\n{cmd}',
        )


class NoTestConfigurationError(cptk.utils.cptkException):
    def __init__(self) -> None:
        super().__init__("Testing workflow isn't configured for the problem")


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

    @property
    def _using_string(self) -> str:
        name = self._problem.recipe.name
        if name is not None:
            return f'using recipe {name!r}'
        return 'using the default recipe'

    def bake(self) -> None:
        """ Bakes (generates) the executable of the current problem solution.
        If the recipe configuration file of the current problem doesn't specify
        a 'bake' option, returns None quietly. """

        if not self._problem.recipe.bake:
            return

        location = self._problem.location
        System.log(f'Baking has begun ({self._using_string})')
        start = time.time()

        for cmd in self._problem.recipe.bake:
            System.details(cmd)
            res = self._runner.exec(cmd, wd=location, redirect=False)
            if res.code:
                raise BakingError(res.code, cmd)

        seconds = time.time() - start
        System.log(f'Solution is baked! (took {seconds:.02f} seconds)')

    def serve(self) -> None:
        """ Bakes the local problem (if a baking recipe is provided), and serves
        it while piping the standard input to the executable. """

        self.bake()

        cmd = self._problem.recipe.serve
        location = self._problem.location

        System.log(f'Serving solution ({self._using_string})')
        System.details(cmd)
        res = self._runner.exec(cmd, wd=location, redirect=False)
        System.abort(res.code)

    def _load_tests(self) -> dict[str, Test]:
        """ Returns a list of tests where the keys are their names and the
        values are the test details. """

        # TODO: the ideal solution will provide a way for the user to fully
        # configure the way that the test inputs end expectations are stored.
        # For now, we force a standard that uses treats all .in files inside
        # the folder as input files, and all .out files as the expected outputs

        folder = os.path.join(
            self._problem.location,
            self._problem.recipe.test.folder,
        )
        if not os.path.isdir(folder):
            return dict()
        files = [
            item for item in os.listdir(
                folder,
            ) if os.path.isfile(os.path.join(folder, item))
        ]

        inputs = {
            filename[:-len(cptk.constants.INPUT_FILE_SUFFIX)]
            for filename in files
            if filename.endswith(cptk.constants.INPUT_FILE_SUFFIX)
        }

        outputs = {
            filename[:-len(cptk.constants.OUTPUT_FILE_SUFFIX)]
            for filename in files
            if filename.endswith(cptk.constants.OUTPUT_FILE_SUFFIX)
        }

        res = dict()
        for name in inputs.intersection(outputs):
            inpp = os.path.join(folder, name + cptk.constants.INPUT_FILE_SUFFIX)
            with open(inpp, 'r', encoding='utf8') as file:
                inp = file.read()
            outp = os.path.join(folder, name + cptk.constants.OUTPUT_FILE_SUFFIX)
            with open(outp, 'r', encoding='utf8') as file:
                out = file.read()
            res[name] = Test(inp, out)

        return res

    def test(self) -> None:
        """ Bakes (if a baking recipe is provided) and serves the local tests
        that are linked to the problem. """

        if self._problem.recipe.test is None:
            raise NoTestConfigurationError()

        self.bake()
        cmd = self._problem.recipe.serve
        location = self._problem.location
        timeout = self._problem.recipe.test.timeout

        tests = self._load_tests()

        LogFunc = System.title if tests else System.warn
        LogFunc(f'Found {len(tests)} tests')

        passed = 0
        start = time.time()

        for name, test in sorted(tests.items()):
            res = self._runner.exec(
                cmd, wd=location, input=test.input,
                redirect=True, timeout=timeout,
            )

            if res.timed_out:
                System.error('Execution timed out', title=name)
            elif res.code:
                System.error(f'Nonzero exit code {res.code}', title=name)
            elif test.expected is not None and res.outs != test.expected:
                System.error('Output differs from expectation', title=name)
            else:
                System.success('Output matches expectations', title=name)
                passed += 1

        seconds = time.time() - start
        failed = len(tests) - passed
        System.title(
            f'{passed} passed and {failed} failed'
            f' in {seconds:.2f} seconds',
        )

        System.abort(1 if failed else 0)
