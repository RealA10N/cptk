from typing import List
from typing import Optional

import cptk.commands
from cptk.core.system import System
from cptk.utils import cptkException

try:
    from colorama import init, deinit
except ImportError:
    init, deinit = lambda: None, lambda: None


def main(args: Optional[List[str]] = None) -> int:

    code = 0  # os.EX_OK

    try:
        init(autoreset=True)
        cptk.commands.collector.run(args)

    except cptkException as err:
        System.error(err)
        code = 65  # os.EX_DATAERR

    except Exception as err:
        System.unexpected_error(err)
        code = 70  # os.EX_SOFTWARE

    finally:
        deinit()
        return code


__all__ = ['main']


if __name__ == '__main__':
    raise SystemExit(main())
