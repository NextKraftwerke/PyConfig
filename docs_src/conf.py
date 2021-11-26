# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
from datetime import date
from pathlib import Path

from setuptools.config import read_configuration

project_root = Path(__file__).parent.parent


# -- Path setup --------------------------------------------------------------

sys.path.insert(0, str(project_root.absolute()))


# -- Project information -----------------------------------------------------

metadata = read_configuration(str(project_root / "setup.cfg"))["metadata"]

project = "PyConfig"
author = metadata["author"]
# noinspection PyShadowingBuiltins
copyright = f"{date.today().year} by {author}"
release = metadata["version"]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.githubpages"]

autodoc_default_options = {
    "imported-members": False,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "python_docs_theme"
