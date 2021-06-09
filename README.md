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

**STL;INRAOT (Still Too Long; I'm Not Reading All Of That):** Like `configparser` but, like, waaay cooler. And safer. And with dot-completion.

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

PyConfig ist meant to be used in _applications_, not _libraries_. Most likely you're using `pipenv` to manage your dependencies, so just add something like
```
# demo/Pipfile
...

[packages]
...
nx_config = ">= x.y.z, <x+1" 
```
to your Pipfile, `pipenv lock` and `pipenv install`.

### Create a config class and its sections classes

Add a new file `config.py` to your app. In it, you'll define a few "section classes", which are subclasses of `ConfigSection`, one "config class", which is a subclass of `Config`, and then initialize a global instance of it (see below why this global instance is okay):

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

Here we make it configurable:
- How many exclamation marks are added after "world" or the user's name.
- Whether the whole greeting is printed in upper case letters or not.
- Which web service will be used to get the weather data (rain probability).
- User credentials for the weather service.
- The client-side timeout for requests to the weather service.

Note that the `username` and `password` are of optional types, i.e., can be None (some weather services might be free). Also, some entries in each section have a default value, while others don't (which means the user must provide a value through a config file or an environment variable).

We see here the `URL` and `SecretString` types. The values of such entries are simply strings. These types are used to convey intent to the user and allow PyConfig to perform validations and other special behaviour. For example, an entry of type `SecretString` is not allowed to have a default value (unless it is optional and the default value is `None`). Furthermore, when you print a config or just a section, entries of type `SecretString` will be replaced with asterisks `"*****"`.

The methods annotated with `@validate` will be called automatically right after the config is loaded (ideally at the startup of your app). Each is used to validate an individual section and sections can have multiple validators.

The combination of the entry `timeout_s` and the method `timeout` above helps us avoid ambiguity for the users (it's clear they must provide a timeout value _in seconds_) while being able to work with a unit-agnostic type in our code (`timedelta`).

Finally, the use of a global config object may seem dangerous (especially in python). However, `Config` and `ConfigSection` objects are always* immutable, so there's no global _state_ to worry about. (*: There are two ways in which the contents of the config can be mutated. One is when loading with `fill_config` or `fill_config_from_path`. The other is with `test_utils.update_section`. You can quickly check that the loading functions are used only once and only at startup. Using the `test_utils` module in production code should be entirely forbidden in your project.)

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

from demo.config import DemoConfig, config
from demo.greet import greet
from nx_config import add_cli_options, resolve_config_path, fill_config_from_path

parser = ArgumentParser()
parser.add_argument("--name")
add_cli_options(parser, config_t=DemoConfig)
args = parser.parse_args()

fill_config_from_path(config, path=resolve_config_path(cli_args=args))

greet(name=args.name or "world")
```

The magic here happens in `fill_config_from_path`. This function will read a configuration file and fill the `config` object's entries with the corresponding values. The path can be hard-coded (not recommended) or you can use `resolve_config_path()` without arguments, in which case the path is provided through the `CONFIG_PATH` environment variable (better) or, as in this example, you can use an `argparse.ArgumentParser` to allow the user to provide the config-path as a CLI argument. The helper `add_cli_options` will add the option `--config-path` (among other things), which `resolve_config_path` will try to read. If the user does not provide a path on the command line, `resolve_config_path` will still use the `CONFIG_PATH` environment variable as a fallback.

The format of the config file will be determined by the path's extension (e.g. '.yaml' for YAML). Note that it's fine (and a common practice) to not provide a config file at all (neither through the CLI nor through the environment variable). In this case, the configuration values will be read from environment variables named `SECTIONNAME__ENTRYNAME` (double underscore!). Even if a config file is provided, values can still be overriden through these environment variables, as we'll see below.

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

Most developers working on those projects knew it was a bad idea and knew how to avoid it (e.g. get the path from a CLI argument or from an environment variable) but A) these solutions would require a bit of extra work and B) they would require teaching the user how to provide the config path... for each application!

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

Some might argue that in the example above we shouldn't have created a global `config` object that's just _loaded_ at startup, but instead we should have created and loaded a `config` object in `__main__.py` and then injected it into the `greet` call. In most cases, I'd agree with this advice. But it is aimed at avoiding global _state_, i.e., global variables that can be read and modified from anywhere in the code, usually causing trouble.

In the case of `Config` instances we don't have to worry*. The config object, each of its sections and each their entries are all immutable** so the `config` object is just a namespace for some constants. The supported types for section entries are also immutable, including the supported collection types `tuple` and `frozenset`.

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

Clearly, there are two ways to mutate a `config` object. One is when you load it, of course. The other is via `test_utils.update_section`. But you can easily scan your project for uses of `fill_config`/`fill_config_from_path` to make sure there is one and only one such call and it's right at the app's startup. Similarly, you can scan your project for uses of `test_utils` to make sure all occurrences are in your directories for tests.

_* and **: Of course, this is python, so there's always a way to cheat by messing with the internal attributes of configs and sections. Let's just assume all contributors to your project are grown ups._

### Automatic validation and failing at startup

### Secrets

### Config file formats

### Documenting configuration options

### Attributes instead of strings

### Handy configuration through environment variables



.

.

.

.

.

.

.

.

.
