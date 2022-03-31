from __future__ import annotations

import cptk.commands
from cptk.core.system import System
from cptk.utils import cptkException


def main(args: list[str] | None = None) -> int:

    code = 0  # os.EX_OK

    try:
        from colorama import deinit
        from colorama import init
        init()
    except ModuleNotFoundError:
        pass  # Colorama is required only on windows

    try:
        cptk.commands.collector.run(args)

    except SystemExit as err:
        # argparse throws a SystemExit if fails to parse arguments or
        # if some arguments are invalid. The System.abort function throws an
        # SystemExit exception too.
        code = err.code

    except KeyboardInterrupt:
        System.error('Manually interrupted')
        code = 130

    except cptkException as err:
        System.error(err)
        code = 65  # os.EX_DATAERR

    except Exception as err:
        System.unexpected_error(err)
        code = 70  # os.EX_SOFTWARE

    finally:
        deinit()
        raise SystemExit(code)


if __name__ == '__main__':
    main()
