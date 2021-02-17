[![License](https://img.shields.io/github/license/NextKraftwerke/PyConfig?style=flat&labelColor=303030&color=c00000)](https://github.com/NextKraftwerke/PyConfig/blob/main/LICENSE)
[![Status (main)](https://img.shields.io/github/workflow/status/NextKraftwerke/PyConfig/tests+coverage/main?label=tests%2Bcoverage&logo=github&style=flat&labelColor=303030&logoColor=a0a0a0)](https://github.com/NextKraftwerke/PyConfig/actions?query=workflow%3Atests%2Bcoverage+branch%3Amain)
![Release](https://img.shields.io/github/v/release/NextKraftwerke/PyConfig?include_prereleases&sort=semver&style=flat&labelColor=303030&color=c00000)

# PyConfig

## README Plan

1. One sentence description.
1. One paragraph description.
1. Short, basic example without too much explanation or details but showing the two approaches with the global config and with dependency injection from main.
1. Motivation (take a look at the confluence page and the woninchen presentation).
1. No mutable global state. Yes, if you decide to use the global config testing becomes harder and you have the issue that you have to remember to initialize it before using it, but _then_ it is immutable (-ish, with the exception of the test util and repeated initialization, but you can easily scan the codebase to make sure those don't happen). And if you choose to use dependency injection there's no global config at all, no initialization worries etc.
1. Why only Config+Sections+Entries? .ini and .env. What about really complex configs? Use several config classes and your own CLI args.
1. This library is only half of the solution. The rest must come from the user. Here are some best practices: Dependency injection; no hard-coded filenames and paths, unless they're fallbacks; Never use `fill_from_file` except for the one time in `__main__`. Never use `test_utils` in production code. Include the config or the relevant parts (e.g. a section) in log messages. Always use `nx_config.SecretString` for secrets. Always use `nx_config.URL` for URLs. Always use `pathlib.Path` for paths. Always use `uuid.UUID` for UUIDs. Always use `datetime.datetime` for dates+times. Always use `typing.Tuple[T, ...]`, `typing.FrozenSet[T]`, `tuple[T, ...]` (python 3.9) or `frozenset[T]` (python 3.9) for lists of values (instead of e.g. comma-separated values in a string). Document entries and sections (and configs if using more than one class). Always use units in entry names if their values have units. For entries with units, try to provide a unitless getter. Use `test_utils` to set up configs for tests (this is faster than parsing files, it's guaranteed to be checked in, and places the values right next to where they're used). Don't write config classes for libraries, but rather for applications (although libraries _can_ provide _section_ classes for convenience). Use `@validate` instead of manually validating the config after it's filled, since this places the conditions for correctness right next to the section-class definitions (for readability) and also guarantees that the validation will be performed in all (including future) entry-points of the application (where someone might forget to manually validate).
1. Installation.
1. Detailed documentation.
