========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-krakenexapi/badge/?style=flat
    :target: https://readthedocs.org/projects/python-krakenexapi
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/Querela/python-krakenexapi.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Querela/python-krakenexapi

.. |requires| image:: https://requires.io/github/Querela/python-krakenexapi/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/Querela/python-krakenexapi/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/Querela/python-krakenexapi/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/Querela/python-krakenexapi

.. |codecov| image:: https://codecov.io/gh/Querela/python-krakenexapi/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Querela/python-krakenexapi

.. |version| image:: https://img.shields.io/pypi/v/krakenexapi.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/krakenexapi

.. |wheel| image:: https://img.shields.io/pypi/wheel/krakenexapi.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/krakenexapi

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/krakenexapi.svg
    :alt: Supported versions
    :target: https://pypi.org/project/krakenexapi

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/krakenexapi.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/krakenexapi

.. |commits-since| image:: https://img.shields.io/github/commits-since/Querela/python-krakenexapi/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/Querela/python-krakenexapi/compare/v0.0.0...master



.. end-badges

A Kraken Exchange API adapter.

* Free software: MIT license

Installation
============

::

    pip install krakenexapi

You can also install the in-development version with::

    pip install https://github.com/Querela/python-krakenexapi/archive/master.zip


Documentation
=============


https://python-krakenexapi.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
