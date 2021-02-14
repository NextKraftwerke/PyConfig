from pathlib import Path

from setuptools import setup

with (Path(__file__).parent / "README.md").open("r") as h:
    _long_description = h.read()

setup(
    name="nx_config",
    version="0.2.0",
    install_requires=[],
    python_requires=">=3.6, <4",
    author="Tomás Silveira Salles",
    description="",  # TBD
    long_description=_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NextKraftwerke/PyConfig",
    classifiers=[],  # TBD
    license="",  # TBD
    keywords=[],  # TBD
)
