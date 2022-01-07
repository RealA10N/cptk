import os


class System:

    GRAY = '\u001b[90m'
    RESET = '\u001b[0m'

    @classmethod
    def run(cls, cmd: str) -> None:
        print(cls.GRAY + cmd + cls.RESET)
        os.system(cmd)
