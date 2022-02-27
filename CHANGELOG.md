# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0a3] - 28.2.2022

### Fixed

- Default configurations and project structures are now bundled with the wheel
  release.
  - This resolves an `UNEXPECTED ERROR` when trying to run the `cptk init`
    subcommand for wheel installs (including ones provided by `pip` from PyPI).

## [0.1.0a2] - 26.2.2022

This alpha release adds the `cptk test` subcommand to cptk! 🥳

Starting from this release the project configuration files supports a new
field called `test`. It will be automatically created for you when you
initialize a new cptk project using `cptk init`, and using it cptk will know
where to store the scraped sample tests when cloning problems.

By default, running `cptk test` will try and run the tests for the last problem
that is known to cptk. It is also easy to add your custom test cases that will
run when executing `cptk test`: just add `.in` and `.out` text files to the
problem's testing folder!

For more information and a full tutorial on the `cptk test` subcommand,
you are more than welcome to visit our [wiki page](https://github.com/RealA10N/cptk/wiki).

### Added

- The `cptk test` subcommand!
  - Optional `test` field for each recipe in the `recipes.cptk.yaml` configuration file
  - Optional `clone.recipe.test` field in the `project.cptk.yaml` configuration file


## [0.1.0a1] - 16.2.2022

### Fixed

- Default templates are now bundled with the package,
  which fixes the bug in `cptk init`.

## [0.1.0a0] - 15.2.2022

The first (alpha) release of cptk! 🥳
Feel free to use the software and report any bugs that you find!
Enjoy and have a nice day! 😃

### Added

- Supported commands are: `cptk initialize`, `cptk clone`, `cptk move`,
  `cptk bake` and `cptk serve`.

[0.1.0a3]: https://github.com/RealA10N/cptk/releases/tag/v0.1.0a3
[0.1.0a2]: https://github.com/RealA10N/cptk/releases/tag/v0.1.0a2
[0.1.0a1]: https://github.com/RealA10N/cptk/releases/tag/v0.1.0a1
[0.1.0a0]: https://github.com/RealA10N/cptk/releases/tag/v0.1.0a0
