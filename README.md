[![License](https://img.shields.io/github/license/NextKraftwerke/PyConfig?style=flat&labelColor=303030&color=c00000)](https://github.com/NextKraftwerke/PyConfig/blob/main/LICENSE)
[![Status (main)](https://img.shields.io/github/workflow/status/NextKraftwerke/PyConfig/tests+coverage/main?label=tests%2Bcoverage&logo=github&style=flat&labelColor=303030&logoColor=a0a0a0)](https://github.com/NextKraftwerke/PyConfig/actions?query=workflow%3Atests%2Bcoverage+branch%3Amain)
![Lines of code](https://img.shields.io/tokei/lines/github/NextKraftwerke/PyConfig?label=lines%20of%20code&style=flat&labelColor=303030&color=606060)
[![Coverage](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/NextKraftwerke/PyConfig/main/.github/stats/coverage.latest.json&label=coverage&query=$.totals.rounded_percent_covered&style=flat&labelColor=303030&suffix=%&color=f09030)](https://github.com/NextKraftwerke/PyConfig/blob/main/.github/stats/coverage.latest.json)
![GitHub issues](https://img.shields.io/github/issues-raw/NextKraftwerke/PyConfig?style=flat&labelColor=303030)
![Python versions](https://img.shields.io/pypi/pyversions/pandas?style=flat&labelColor=303030)
![Latest](https://img.shields.io/github/v/release/NextKraftwerke/PyConfig?include_prereleases&sort=semver&style=flat&labelColor=303030&color=00959f&label=latest)
![PyPI](https://img.shields.io/pypi/v/pandas?style=flat&labelColor=303030)

# PyConfig

**TL;DR:** PyConfig helps you write configurable applications with ease and takes care of config validation at loading time. It allows the end-user to choose their configuration language and whether to use files or environment variables or both. The library is designed to make best practices the natural way to do things and to remove the need to write and maintain documentation of the configuration options.

**STL;INRAOT (Still Too Long; I'm Not Reading All Of That):** Like `configparser` but, like, waaay cooler. And safer. And with dot-autocompletion.

## Introduction by example

You can find a complete guide of the library further down, but for simple use cases it might suffice to just look at an example, so that's how we'll start.

In this example we pretend to build an app that greets the user and exits. The user can provide a name through the `--name` argument. The greeting also includes a suggestion to go out or stay home depending on whether it's going to rain.

```commandline
$ python -m demo
Hello, world! It's a beautiful day outside. Have fun!
$ python -m demo --name Dave
Hello, Dave! (you should probably stay home today...)
```

### Install PyConfig (package name `nx_config`)

PyConfig is meant to be used in _applications_, not _libraries_ (more on this later). It is a PyPI package so you can easily install it with `pip`:

```commandline
$ pip install nx_config
```

Or with `poetry`:

```commandline
$ poetry add nx_config
```

### Create a config class and its sections classes

Add a new file `config.py` to your app. In it, you'll define a few "section classes", which are subclasses of `ConfigSection`, one "config class", which is a subclass of `Config`, and then initialize a global instance of it (see below why this is okay):

```python
# demo/config.py
from datetime import timedelta
from typing import Optional

from nx_config import Config, ConfigSection, URL, SecretString, validate


class GreetingSection(ConfigSection):
    num_exclamation_marks: int = 1
    all_caps: bool = False

    @validate
    def positive_exclamation_marks(self):
        if self.num_exclamation_marks <= 0:
            raise ValueError("Number of exclamation marks must be positive!")


class WeatherSection(ConfigSection):
    service_url: URL
    username: Optional[str] = None
    password: Optional[SecretString] = None
    timeout_s: float = 70.0

    @validate
    def username_and_password_go_together(self):
        if (self.username is None) ^ (self.password is None):
            raise ValueError("Must either provide both username and password or neither of them!")

    def timeout(self) -> timedelta:
        return timedelta(seconds=self.timeout_s)


class DemoConfig(Config):
    greet: GreetingSection
    weather: WeatherSection


config = DemoConfig()
```

Here we make the following configurable:
- How many exclamation marks are added after "world" or the user's name.
- Whether the whole greeting is printed in upper case letters or not.
- Which web service will be used to get the weather data (rain probability).
- User credentials for the weather service.
- The client-side timeout for requests to the weather service.

Note that the `username` and `password` are of optional types, i.e., can be None (some weather services might be free). Also, some entries in each section have a default value, while others don't (which means the user must provide a value through a config file or an environment variable).

We see here the `URL` and `SecretString` types. The values of such entries are simply strings. These types are used to convey intent to the user and allow PyConfig to perform validations and other special behaviour. For example, an entry of type `SecretString` is not allowed to have a default value (unless it is optional and the default value is `None`). Furthermore, when you print a config or just a section, entries of type `SecretString` will be replaced with asterisks `"*****"`.

The methods annotated with `@validate` will be called automatically right after the config is loaded (ideally at the startup of your app). Each is used to validate an individual section and sections can have multiple validators.

The combination of the entry `timeout_s` and the method `timeout` above helps us avoid ambiguity for the users (it's clear they must provide a timeout value _in seconds_) while being able to work with a unit-agnostic type in our code (`timedelta`).

Finally, the use of a global config object may seem dangerous (especially in python), but `Config` and `ConfigSection` objects are always* immutable, so there's no global _state_ to worry about.

_*: There are two ways in which the contents of the config can be mutated. One is when loading with `fill_config` or `fill_config_from_path`. The other is with `test_utils.update_section`. You can quickly find all usages of these functions in your repository. Loading functions are ideally used only once and only at startup. Using the `test_utils` module in production code should be entirely forbidden._

### Use the configuration in your code

In the `greet.py` module we use our config several times:

```python
# demo/greet.py
from datetime import timedelta
from typing import Mapping

from demo.config import config


def _get_rain_probability(
    url: str, params: Mapping[str, str], timeout: timedelta
) -> float:
    ...


def greet(name: str):
    msg = f"Hello, {name}" + ("!" * config.greet.num_exclamation_marks)  # <===

    if config.greet.all_caps:  # <===
        msg = msg.upper()

    if config.weather.username is None:  # <===
        params = {}
    else:
        params = {
            "username": config.weather.username,  # <===
            "password": config.weather.password,  # <===
        }

    rain_prob = _get_rain_probability(
        url=config.weather.service_url,  # <===
        params=params,
        timeout=config.weather.timeout(),  # <===
    )

    if rain_prob > 0.5:
        msg += " (you should probably stay home today...)"
    else:
        msg += " It's a beautiful day outside. Have fun!"

    print(msg)
```

Your IDE will probably offer auto-completion for section names and entries within sections. In contrast to the usual approach with dictionaries (e.g. with `configparser`), it's very unlikely that you'll make a typing error this way. And even if you do, you'll be trying to get an attribute that doesn't exist and in this case the attributes of both configs and sections are determined at class declaration (instead of depending on the user's config file) and cannot be changed afterwards. This means that if you test your code and don't get an `AttributeError`, you can be certain you won't get an `AttributeError` in production, regardless of what your users write in their configuration files.

### Load configuration on startup

```python
# demo/__main__.py
from argparse import ArgumentParser

from demo.config import config
from demo.greet import greet
from nx_config import add_cli_options, resolve_config_path, fill_config_from_path

parser = ArgumentParser()
parser.add_argument("--name")
add_cli_options(parser, config_t=type(config))
args = parser.parse_args()

fill_config_from_path(config, path=resolve_config_path(cli_args=args))

greet(name=args.name or "world")
```

The magic here happens in `fill_config_from_path`. This function will read a configuration file and fill the `config` object's entries with the corresponding values. The path can be hard-coded (not recommended) or you can use `resolve_config_path()` without arguments, in which case the path is provided through the `CONFIG_PATH` environment variable (better) or, as in this example, you can use an `argparse.ArgumentParser` to allow the user to provide the config-path as a CLI argument. The helper `add_cli_options` will add the option `--config-path` (among other things), which `resolve_config_path` will try to read. If the user does not provide a path on the command line, `resolve_config_path` will still use the `CONFIG_PATH` environment variable as a fallback.

The format of the config file will be determined by the path's extension (e.g. `.yaml` for YAML). Note that it's fine (and a common practice) to not provide a config file at all (neither through `--config-path` nor through `CONFIG_PATH`). In this case, the configuration values will be read from environment variables named `SECTIONNAME__ENTRYNAME` (double underscore!). Even if a config file is provided, values can still be overriden through these environment variables, as we'll see below.

### Write a configuration file

The `add_cli_options` function above also adds a `--generate-config` option that prints out a template config file and exits. It is intended to be used as follows:

```commandline
$ python -m demo --generate-config=yaml > demo/config.yaml
```

which in this example results in the following file:

```yaml
# demo/config.yaml
greet:
  #num_exclamation_marks:
  #all_caps:
weather:
  service_url:
  #username:
  #password:
  #timeout_s:
```

All entries and all sections are present, but entries that have a default value are commented-out, so you know exactly what you _need_ to fill out for the program to run. We can fill out the `service_url` in this file, say 

```yaml
  service_url: www.weatherservice24.com/rain
```

and use it to run our app. We can still change other entries (or even override values from this file) using canonically named environment variables such as `GREET__NUM_EXCLAMATION_MARKS`:

```commandline
$ export GREET__NUM_EXCLAMATION_MARKS=5
$ python -m demo --name Dave --config-path demo/config.yaml
Hello, Dave!!!!! It's a beautiful day outside. Have fun!
```

## Why?

What's so great about PyConfig? Why should you bother learning to use yet another library when `configparser` already does a pretty good job? Also: There are **dozens** of configuration libraries for python already! What makes PyConfig different?

### Avoiding hard-coded paths

The `configparser.ConfigParser.read` method takes a string or `PathLike` (or several) as argument. I have seen and worked on many, many projects where this argument was written as a hard-coded, version-controlled string. This is, of course, in most cases a bad idea. It makes it difficult to try out the code locally, or deploy it on multiple servers automatically, can result in clashes with different applications using the same path (and therefore making it impossible to configure them independently), cause headaches due to missing permissions and so on. It also makes it annoying and slow to use different configurations for different runs of the same application.

Most developers working on those projects knew it was a bad idea and knew how to avoid it (e.g. get the path from a CLI argument or from an environment variable) but (a) these solutions would require a bit of extra work and (b) they would require teaching the user how to provide the config path... for each application!

PyConfig offers two really simple solutions to this, making the best practice _nearly_ the easiest thing to do. First, you can use the function `resolve_config_path()` with no arguments. This will return a `pathlib.Path` from the value of the `CONFIG_PATH` environment variable if defined, and `None` otherwise. With a little extra effort, by using an `argparse.ArgumentParser` and the function `add_cli_options(<parser>, config_t=<config_class>)` you can allow your end-users to provide a config path either through the `--config-path` CLI option or the `CONFIG_PATH` environment variable:

```python
parser = ArgumentParser()
add_cli_options(parser, config_t=DemoConfig)
args = parser.parse_args()
path = resolve_config_path(cli_args=args)
```

If you have multiple apps sharing environment variables or you use multiple config classes for a single app (should rarely be necessary), you can add a prefix to both the CLI option and the path environment variable:

```python
parser = ArgumentParser()
add_cli_options(parser, prefix="demo", config_t=DemoConfig)
args = parser.parse_args()
path = resolve_config_path("demo", cli_args=args)
```

Now the CLI option `--demo-config-path` and the environment variable `DEMO_CONFIG_PATH` will be used instead. Most importantly, this solution offers a standardized way for users to provide config files, through arguments that follow a simple naming convention, for all apps using PyConfig.

### Immutability

Some might argue that in the example above we shouldn't have created a _global_ `config` object that's just _loaded_ at startup, but instead we should have created and loaded a `config` object in `__main__.py` and then injected it into the `greet` call. In most cases, I'd agree with this advice. But it is aimed at avoiding global _state_, i.e., global variables that can be read and modified from anywhere in the code, usually causing trouble.

In the case of `Config` instances we don't have to worry*. The config object, each of its sections and each their entries are all immutable** so the instance is just a namespace for some constants. The supported types for section entries are also immutable, including the supported collection types `tuple` and `frozenset`.

Many configuration libraries allow the config object to be modified freely at any time, which is particularly problematic with long-running services. If a critical error or even a crash occurs, you don't have any guarantees that the configuration you provided at startup is still valid. The configuration being used by the application might be completely different from the values you see in your configuration files. This makes it difficult to understand and replicate bugs. With PyConfig it's very easy to check whether the config can ever change by searching for uses of `fill_config` and `fill_config_from_path` in the project. Ideally it will be loaded once and only once at startup but even if your app allows for config updates while running, the logic coordinating this will at least be easy to find. Also, check out the section on 'logging' below, which can be very helpful to make your app easy to debug.

To facilitate testing with different configurations, we've added the function `test_utils.update_section` (can only be imported through the module `test_utils`, not directly from `nx_config`):

```python
# tests/test_greeting.py
from unittest import TestCase
from nx_config.test_utils import update_section
from demo.config import config

class DemoTests(TestCase):
    def setUp(self):
        ...  # load your base config values for testing

    def test_something(self):
        update_section(config.greet, num_exclamation_marks=7)
        ...  # call code that uses config
```

Again, there are exactly two ways to mutate a `config` object. One is when you load it, of course. The other is via `test_utils.update_section`. But you can easily scan your project for uses of `fill_config`/`fill_config_from_path` to make sure there is one and only one such call and it's right at the app's startup, and you can scan your project for uses of `test_utils` to make sure all occurrences are in your directories for tests.

_* and **: Of course... this is python. There are dark ways to cheat by messing with the internal attributes of configs and sections. Let's just assume all contributors to your project are grown ups._

### Config file formats

Unlike many configuration libraries, PyConfig completely separates your code (and the modelling of your configuration options) from the input formats the end-user is allowed to use for configuration. You only write python and don't need to think for a second about YAML, INI, JSON, .ENV or whatever.

In this early version, PyConfig only supports YAML and environment variables but very soon we'll add support for INI files and the library is designed to be easily extensible to add more supported formats. Once INI is supported, we'll be listening to the community to see what other formats would be good candidates. And as a developer using PyConfig, all you'll need to do is install a new version and your end-users immediately have the option to use the newly supported input format. _Your code is config-format-agnostic_.

This freedom of choice can also be interesting for companies with teams using different programming languages. They have the option of defining a single, company-wide "configuration language" to be used in all projects. This is convenient for everyone and allows, for example, the use of centralized configuration files in production (e.g. with credentials to different services, common URLs and so on). And with PyConfig, individual programmers can still pick a different "configuration language" during development and for local testing. 

### Documenting configuration options

One of the biggest advantages of using PyConfig is that the contents of the config model (i.e. which sections it should have, which entries each section should have, what their types should be etc) are defined in code.

With `configparser`, for example, it is common practice to have 3 independent "definitions" of the configuration options. One is the actual usage of the config mapping in the source code, which is spread throughout the repository and not always easy to find. The second is the documentation written for end-users, usually in PDF of markdown format, listing all the sections, entries, types and how to use each entry. The third is sometimes a template INI file that the end-users can copy and then fill out with their chosen values. These 3 "definitions" have to be maintained and kept in sync with each other, which is rarely the case. Very often developers might, for instance, delete some code that used a configuration value, or just use a new config entry, or change the default value of an entry and forget to update the documentation or the INI template. And even if you're extra careful and put a lot of work into keeping your docs up-to-date, experienced end-users will still not trust your docs because they've fallen into that trap enough times in the past already.

Enter: PyConfig. The code, i.e. your class definitions, is the only definition of the configuration options. It is the definitive truth and documents by definition every detail of the config, including types, default values _and validity checks_. And if you add docstrings to the config class and the section classes (and some tools also support docstrings directly below class attributes, so feel free), they are much more likely to be kept up-to-date because they're right next to the code they reference.

If you use the `add_cli_options` utility applied to an `argparse.ArgumentParser`, your end-users get the `--generate-config` CLI option for free, with which they can generate config templates for any supported file format, e.g.:

```commandline
$ python -m demo --generate-config=yaml
greet:
  #num_exclamation_marks:
  #all_caps:
weather:
  service_url:
  #username:
  #password:
  #timeout_s:
```

Another (soon to be implemented) feature is the `--config-help` CLI option, that will also be added automatically through `add_cli_options`. This option will show a message specifically documenting your app's config model, followed by cheat-sheet-style instructions for configuring with PyConfig (as an end-user).

This means all the documentation your app needs (in terms of configuration options) is easily automagically generated from your class definitions and is always up-to-date. Even if you want to have the documentation directly available on your website or on github, you can setup the pipeline to re-generate it after every release. No maintenance needed.

Contributors to your project are even happier: they only have to look at the python code, just the one module, without any additional PDFs or markdown files or webpages, and they're guaranteed to find all relevant, current information there.

### Automatic validation and failing at startup

PyConfig always validates the configuration input against the type-hints used in the `ConfigSection` subclass declaration. In the case of environment variables or INI files, the values are initially interpreted as strings, so "checking the type" means checking that the provided strings can be transformed into the intended types (i.e. the string `"3.14"` is fine for a `float`, but no good for a `UUID`). In the case of YAML or JSON files, for example, there are already standard libraries that parse them into python objects of different types, so only smaller conversions will be made (e.g. `str -> Path` or `list -> frozenset`) depending on the provided type-hints.

Two more out-of-the-box automatic checks are:
* Users must provide a value for every field that doesn't have a default.
* Secrets cannot have default values. They must always be provided by the end-user. (But `Optional[SecretString]` can have default `None`, `tuple[SecretString, ...]` can have default `()` etc.)

On top of these, you can add validating methods (single parameter `self`, no return value) to your section classes through the `@validate` annotation. These methods will be called right after filling in the values for the section in `fill_config` or `fill_config_from_path` (see examples above).

If you use PyConfig and follow the best practice of loading all configuration at the app's startup (and only then), you'll never have to worry about an invalid configuration value causing trouble days after your long-running service went up, in the middle of the night or during your soon-to-be-cut-short vacation. Can you do the same with other configuration libraries? Certainly. PyConfig is just friendly and convenient.

### Logging (and secrets)

Both `Config` and `ConfigSection` subclasses can be very nicely printed with ease. The `__str__` method produces an inline description, while the `__repr__` method gives a multi-line and indented version. Moreover, secrets (i.e. section entries type-annotated as `SecretString`) are automatically masked with asterisks, including optional secrets and collections of secrets.

Here are example outputs using the `DemoConfig` class from above:
```commandline
>>> print(str(config))
DemoConfig(greet=GreetingSection(num_exclamation_marks=1, all_caps=False), weather=WeatherSection(service_url='www.weatherservice24.dummy', username='Dave', password='*****', timeout_s=70.0))
>>> print(str(config.greet))
GreetingSection(num_exclamation_marks=1, all_caps=False)
>>> print(repr(config))
DemoConfig(
    greet=GreetingSection(
        num_exclamation_marks=1,
        all_caps=False,
    ),
    weather=WeatherSection(
        service_url='www.weatherservice24.dummy',
        username='Dave',
        password='*****',
        timeout_s=70.0,
    ),
)
>>> print(repr(config.greet))
GreetingSection(
    num_exclamation_marks=1,
    all_caps=False,
)
```

Having both formats available is very convenient when writing log messages, and indeed you should take advantage of this and log your app's configuration in certain situations. A good idea would be to log the configuration right after it's loaded at startup. Another approach would be to log the configuration whenever a serious error happens (this is more convenient for debugging, having all the necessary information bundled into the error message). It's also convenient to just always (easily) log the entire configuration, instead of trying to guess a subset of its values that you think will be sufficient when debugging. And if you always log entire configs (or at least entire sections), you don't have to worry about accidentally exposing your end-user's secrets.

The choice of which method gets which format was made with debugging in mind. In the REPL, if you just type the object you want to inspect, the result will be printed using `__repr__`:
```commandline
>>> config.weather
WeatherSection(
    service_url='www.weatherservice24.dummy',
    username='Dave',
    password='*****',
    timeout_s=70.0,
)
```

And if you use PyCharm, the "Variables" view on the console and the debugger displays values next to variable names using `__str__`, and the one-line description is much more suitable in that case.

### Attributes instead of strings

Using attributes for sections and section-entries (`cfg.a_section.an_entry`) instead of the mapping style with strings used in many configuration libraries (`cfg["a_section"]["an_entry"]`) is more than just shorter, prettier and easier to type.

Your IDE can help you with dot-autocompletion to (a) present the available sections and section-entries and (b) avoid typing errors. This is especially important because even if your configuration is thoroughly validated at startup, a typing error when _using_ the configuration might only cause trouble much, much later, when no one is watching and ready to take action. (Yes, of course, you'd find such bugs either way if you have 100% code coverage...)

In theory, there's even more the IDE could do. If you still make typing errors in such attributes because you didn't use autocompletion, the static analyser could highlight them and warn you. And if you decide to change the name of a section or section-entry, the IDE could help with automatic refactoring. Both things work more reliably and conveniently with attributes instead of mappings, usually. Unfortunately, we haven't manage to get them to work with PyConfig sections and entries yet. We know this is due to limitations of the IDE and the fact that PyConfig uses a lot of magic behind the scenes, but we're still trying to understand the issue.

Still, autocompletion + shorter + prettier is plenty of reason to prefer the attribute variant.

### Handy configuration through environment variables

There are situations in which configuring apps with files can be annoying, such as when doing quick tests and experiments locally on a terminal and changing just one or two configuration options all the time.

With PyConfig you can _always_ override any configurations from files with environment variables. The standard naming convention is `SECTIONNAME__ENTRYNAME` (yes, double underscore, which makes the separation clearer when the section name or the entry name also contain underscores). In the example above, we've seen how to override the `config.greet.num_exclamation_marks` entry by setting the `GREET__NUM_EXCLAMATION_MARKS` environment variable.

If you have several configs in a single app or several apps sharing some environment variables, it's also possible to use a prefix to make variable names more specific. For example, you could use the environment variable `FOO__GREET__NUM_EXCLAMATION_MARKS` instead, and load the configuration with `fill_config_from_path(config, path=..., env_prefix="FOO")`.

Finally, even the path to the configuration file can be provided through an environment variable, namely `CONFIG_PATH`. Again, it's possible to use a prefix to make this name more specific. For example, you could use the variable `BAR_CONFIG_PATH` instead, and get the path with `resolve_config_path("bar", cli_args=...)`. Note: If you use the `cli_args` argument in this case, `resolve_config_path` will look for the option `--bar-config-path` instead of `--config-path`, so make sure you use the same prefix when adding options to the `argparser.ArgumentParser` by calling `add_cli_options(parser, prefix="bar", config_t=type(config))`.

### Support for the most useful types

After loading the config values, you should ideally be able to use them without having to first convert them into other types. If you have your own unit-agnostic `Temperature` type, for instance, you'll have to work a little harder, ask your end-users for a unit-bound value (e.g. `surface_temp_celsius: float`) and then convert it yourself (e.g. through a method `def surface_temp(self) -> Temperature:` in the same section). But most use cases should be covered by the types already supported by PyConfig (and there might be more on the way).

* **Base** supported types are `int`, `float`, `bool`, `str`, `datetime.datetime`, `uuid.UUID`, `pathlib.Path`, `nx_config.SecretString`, and `nx_config.URL`.
* **Collection** supported types are `typing.Tuple[base, ...]` and `typing.FrozenSet[base]` in all python versions, and `tuple[base, ...]` and `frozenset[base]` for python 3.9 and later (where `base` is one of the **base** supported types above). _Note that the `...` in the tuple types is meant literally here, i.e., they represent tuples of arbitrary length where all elements are of the same type._
* **Optional** supported types are `typing.Optional[base_or_coll]` (where `base_or_coll` is either one of the **base** or one of the **collection** supported types listed above). _Note that optional base types are not allowed as the element type in collections (e.g. `tuple[Optional[int], ...]`)._

## A note on imports

Everything you need from PyConfig for production code can (and ideally should) be imported directly from the `nx_config` module:
```python
from nx_config import Config, ConfigSection, SecretString, fill_config, ...
```
Everything you need from PyConfig for your tests can (and ideally should) be imported directly from the `nx_config.test_utils` module:
```python
from nx_config.test_utils import update_section
```
And that's everything. If you find yourself importing stuff from other submodules: it's probably not meant for you. I've made an effort to keep everything else protected behind underscores, but something may have slipped through, or might slip through in the future.

## A note on configuring libraries vs apps

It usually doesn't make much sense to use configuration from files and environment variables directly into libraries. Configuration should be required from and received by applications, which can then inject any necessary values into library classes and functions. Libraries should at least offer the application the _possibility_ of injecting all relevant values as input parameters. This makes it easier and more convenient to write tests, and can even be important for performance.

I've seen libraries offering classes that parsed configuration files when initialized (using default, hard-coded paths). Very well-informed users would initialize such objects rarely in their applications and keep them around for as long as possible. But most users just assumed initialization would have near-zero cost and created new objects whenever one was needed, unknowingly parsing files and throwing the information away over and over again.

App writers should have the ultimate control over how and when files are read and parsed.

Adding a `Config` subclass to a library is a very bad idea. It would force the app writers to use that class for that specific library and then use a different class for their own configuration options. Adding a `ConfigSection` subclass to a library _can_ be a friendly feature for application writers, who can use such sections in their own `Config` classes. But even that might carry some rigidity with it: Apps might only want to give their users _some_ control over the configuration of a library, but the `ConfigSection` provided will likely give them full control.

Keep it simple. Use PyConfig in applications. Use injection (of every necessary input or configuration value) in libraries.

## Detailed documentation

_TBD. Sorry. Really._

## FAQ

1. _Why can't I nest sections into other sections?_ This was not the easiest design choice. One of the most important requirements when writing PyConfig was that it should support INI files, and those only really support 1 level of nesting. In the end, even though this question is asked fairly often, there are barely any use cases for deeper nesting in configs. And in the few such use cases I've seen, the problem could be elegantly solved by using more than one `Config` subclass in the application.
2. _Why can't I have entries directly in the `Config` subclass? Why must all entries be in a section?_ Firstly, it would add more complexity to the implementation. Secondly, INI doesn't allow entries without sections. Thirdly, this isn't much of an issue, really. You can always just add a `general` section to your config.
3. _Why aren't dictionaries supported as types for section-entries?_ INI. The answer is almost always INI. I've chosen to support the iterable types `tuple` and `frozenset` because it's so common and natural to interpret comma-separated values as sequences, and these types are increadibly helpful in configurations. Moreover, I'd already seen several projects where configuration values were being transformed into sequences via comma-separation, except that developers had to parse those strings themselves, without any help from `configparser`. But there's nothing as simple, elegant and commonplace for dictionaries. Gladly, there's also almost no demand for dictionaries as section-entries.
4. _Regarding the standard naming for environment variables: What happens if I have a section called `foo__bar` with an entry called `baz`, and also a section called `foo` with an entry called `bar__baz`?_ Honestly, I haven't thought about it. Bad things, probably.
5. _Are all these questions really frequently asked, or are you making them up as you go?_ Yes.
