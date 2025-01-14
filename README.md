# perceval-opnfv [![Build Status](https://github.com/chaoss/grimoirelab-perceval-opnfv/workflows/tests/badge.svg)](https://github.com/chaoss/grimoirelab-perceval-opnfv/actions?query=workflow:tests+branch:main+event:push) [![Coverage Status](https://img.shields.io/coveralls/chaoss/grimoirelab-perceval-opnfv.svg)](https://coveralls.io/r/chaoss/grimoirelab-perceval-opnfv?branch=main)  [![PyPI version](https://badge.fury.io/py/perceval-opnfv.svg)](https://badge.fury.io/py/perceval-opnfv)

Bundle of Perceval backends for OPNFV ecosystem.

## Backends

The backends currently managed by this package support the next repositories:

* Functest

## Requirements

 * Python >= 3.9

You will also need some other libraries for running the tool, you can find the
whole list of dependencies in [pyproject.toml](pyproject.toml) file.

## Installation

There are several ways to install perceval-opnfv on your system: packages or source 
code using Poetry or pip.

### PyPI

perceval-opnfv can be installed using pip, a tool for installing Python packages. 
To do it, run the next command:
```
$ pip install perceval-opnfv
```

### Source code

To install from the source code you will need to clone the repository first:
```
$ git clone https://github.com/chaoss/grimoirelab-perceval-opnfv
$ cd grimoirelab-perceval-opnfv
```

Then use pip or Poetry to install the package along with its dependencies.

#### Pip
To install the package from local directory run the following command:
```
$ pip install .
```
In case you are a developer, you should install perceval-opnfv in editable mode:
```
$ pip install -e .
```

#### Poetry
We use [poetry](https://python-poetry.org/) for dependency management and 
packaging. You can install it following its [documentation](https://python-poetry.org/docs/#installation).
Once you have installed it, you can install perceval-opnfv and the dependencies in 
a project isolated environment using:
```
$ poetry install
```
To spaw a new shell within the virtual environment use:
```
$ poetry shell
```

## Examples

### Functest

```
$ perceval functest http://testresults.opnfv.org/test/ --from-date 2017-06-01 --to-date 2017-06-02
```

## License

Licensed under GNU General Public License (GPL), version 3 or later.
