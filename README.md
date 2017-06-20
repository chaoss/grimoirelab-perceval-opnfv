# perceval-opnfv [![Build Status](https://travis-ci.org/grimoirelab/perceval-opnfv.svg?branch=master)](https://travis-ci.org/grimoirelab/perceval-opnfv) [![Coverage Status](https://img.shields.io/coveralls/grimoirelab/perceval-opnfv.svg)](https://coveralls.io/r/grimoirelab/perceval-opnfv?branch=master)

Bundle of Perceval backends for OPNFV ecosystem.

## Backends

The backends currently managed by this package support the next repositories:

* Functest

## Requirements

* Python >= 3.4
* python3-requests >= 2.7
* grimoirelab-toolkit >= 0.1
* perceval >= 0.8

## Installation

To install this package you will need to clone the repository first:

```
$ git clone https://github.com/grimoirelab/perceval-opnfv.git
```

In this case, [setuptools](http://setuptools.readthedocs.io/en/latest/) package
will be required. Make sure it is installed before running the next commands:

```
$ pip3 install -r requirements.txt
$ python3 setup.py install
```

## Examples

### Functest

```
$ perceval functest http://testresults.opnfv.org/test/ --from-date 2017-06-01 --to-date 2017-06-02
```

## License

Licensed under GNU General Public License (GPL), version 3 or later.
