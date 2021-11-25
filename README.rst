.. image:: https://img.shields.io/github/license/NextKraftwerke/PyConfig?style=flat&labelColor=303030&color=c00000
  :target: https://github.com/NextKraftwerke/PyConfig/blob/main/LICENSE
  :alt: License
.. image:: https://img.shields.io/github/workflow/status/NextKraftwerke/PyConfig/tests+coverage/main?label=tests%2Bcoverage&logo=github&style=flat&labelColor=303030&logoColor=a0a0a0
  :target: https://github.com/NextKraftwerke/PyConfig/actions?query=workflow%3Atests%2Bcoverage+branch%3Amain
  :alt: Status (main)
.. image:: https://img.shields.io/tokei/lines/github/NextKraftwerke/PyConfig?label=lines%20of%20code&style=flat&labelColor=303030&color=606060
  :target: https://github.com/NextKraftwerke/PyConfig
  :alt: Lines of code
.. image:: https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/NextKraftwerke/PyConfig/main/.github/stats/coverage.latest.json&label=coverage&query=$.totals.rounded_percent_covered&style=flat&labelColor=303030&suffix=%&color=f09030
  :target: https://github.com/NextKraftwerke/PyConfig/blob/main/.github/stats/coverage.latest.json
  :alt: Coverage
.. image:: https://img.shields.io/github/issues-raw/NextKraftwerke/PyConfig?style=flat&labelColor=303030
  :target: https://github.com/NextKraftwerke/PyConfig/issues
  :alt: GitHub issues
.. image:: https://img.shields.io/pypi/pyversions/nx-config?style=flat&labelColor=303030
  :target: https://github.com/NextKraftwerke/PyConfig/blob/main/setup.cfg
  :alt: Python versions
.. image:: https://img.shields.io/github/v/release/NextKraftwerke/PyConfig?include_prereleases&sort=semver&style=flat&labelColor=303030&color=00959f&label=latest
  :target: https://github.com/NextKraftwerke/PyConfig/releases
  :alt: Latest
.. image:: https://img.shields.io/pypi/v/nx-config?style=flat&labelColor=303030
  :target: https://pypi.org/project/nx-config/
  :alt: PyPI

.. TODO: Add links to the following references once we have a stable docs URL.
.. _Config: TODO
.. _ConfigSection: TODO
.. _URL: TODO
.. _SecretString: TODO
.. _@validate: TODO
.. _fill_config: TODO
.. _fill_config_from_path: TODO
.. _test_utils.update_section: TODO
.. _add_cli_options: TODO
.. _resolve_config_path: TODO
.. _docs: TODO

################################################################################
PyConfig
################################################################################

TL;DR
    PyConfig helps you write configurable applications with ease and takes care of config validation at loading time. It allows the end-user to choose their configuration language and whether to use files or environment variables or both. The library is designed to make best practices the natural way to do things and to remove the need to write and maintain documentation of the configuration options.

STL;INRAOT (Still Too Long; I'm Not Reading All Of That)
    Like `configparser`_ but, like, waaay cooler. And safer. And with dot-autocompletion.

.. include:: docs/intro.rst

Detailed documentation
================================================================================

The full docs for PyConfig are *still very much under construction* and can be found `here`__.

.. __: docs_

FAQ
================================================================================

1. Why can't I nest sections into other sections?
    This was not the easiest design choice. One of the most important requirements when writing PyConfig was that it should support INI files, and those only (really) support 1 level of nesting. In the end, even though this question is asked fairly often, there are barely any use cases for deeper nesting in configs. And in the few such use cases I've seen, the problem could be elegantly solved by using more than one `Config`_ subclass in the application.
2. Why can't I have entries directly in the `Config`_ subclass? Why must all entries be in a section?
    Firstly, it would add more complexity to the implementation. Secondly, INI doesn't allow entries without sections. Thirdly, this isn't much of an issue, really. You can always just add a *general* section to your config.
3. Why aren't dictionaries supported as types for section-entries?
    INI. The answer is almost always INI. I've chosen to support the iterable types ``tuple`` and ``frozenset`` because it's so common and natural to interpret comma-separated values as sequences, and these types are incredibly helpful in configurations. Moreover, I'd already seen several projects where configuration values were being transformed into sequences via comma-separation, except that developers had to parse the strings themselves.

    For dictionaries, there's no such simple, elegant and commonplace representation. Gladly, there's also very little demand for dictionaries as section-entries.
4. Regarding the standard naming for environment variables: What happens if I have a section called ``foo__bar`` with an entry called ``baz``, and also a section called ``foo`` with an entry called ``bar__baz``?
    Honestly, I haven't thought about it. Bad things, probably.
5. Are all these questions really frequently asked, or are you making them up as you go?
    Yes.
