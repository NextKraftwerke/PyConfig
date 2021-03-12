from pathlib import Path

from setuptools import setup

with (Path(__file__).parent / "README.md").open("r") as h:
    _long_description = h.read()

setup(
    name="nx_config",
    version="0.2.0",
    packages=["nx_config", "nx_config._core"],
    install_requires=[],
    extras_require={
        "tests": [],
        "tox": ["tox >=3.21.4, <4"],
        "coverage": ["coverage >=5.4, <6"],
    },
    python_requires=">=3.6, <3.10",
    author="Tomás Silveira Salles",
    author_email="30598365+tomasssalles@users.noreply.github.com",
    description=(
        "A convenient way to configure python applications that makes it easy"
        " and natural to follow best practices and solves a variety of common"
        " issues encountered when using e.g. the 'configparser' library."
    ),
    long_description=_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NextKraftwerke/PyConfig",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
    ],
    keywords=["configuration", "settings", "yaml", "toml", "ini", "env"],
)
