========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |ghaw-tox| |travis| |requires| |ghaw-dco| |black|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations| |ghaw-pypi|
        | |license| |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-krakenexapi/badge/?style=flat
    :target: https://readthedocs.org/projects/python-krakenexapi
    :alt: Documentation Status

.. |ghaw-tox| image:: https://github.com/Querela/python-krakenexapi/workflows/Python%20tox%20Tests/badge.svg
    :alt: GitHub Actions Workflow - Tox Tests
    :target: https://github.com/Querela/python-krakenexapi/actions?query=workflow%3A%22Python+tox+Tests%22

.. |ghaw-dco| image:: https://github.com/Querela/python-krakenexapi/workflows/Check%20DCO/badge.svg
    :alt: GitHub Actions Workflow - Check DCO
    :target: https://github.com/Querela/python-krakenexapi/actions?query=workflow%3A%22Check+DCO%22

.. |ghaw-pypi| image:: https://github.com/Querela/python-krakenexapi/workflows/Upload%20Python%20Package/badge.svg
    :alt: GitHub Actions Workflow - Publish tagged version to PyPI
    :target: https://github.com/Querela/python-krakenexapi/actions?query=workflow%3A%22Upload+Python+Package%22

.. |travis| image:: https://api.travis-ci.com/Querela/python-krakenexapi.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/Querela/python-krakenexapi

.. |requires| image:: https://requires.io/github/Querela/python-krakenexapi/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/Querela/python-krakenexapi/requirements/?branch=master

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style: black
    :target: https://github.com/psf/black

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

.. |license| image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :alt: MIT license
    :target: https://github.com/Querela/python-krakenexapi/blob/master/LICENSE

.. |commits-since| image:: https://img.shields.io/github/commits-since/Querela/python-krakenexapi/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/Querela/python-krakenexapi/compare/v0.0.1...master

.. end-badges

A Kraken Exchange API adapter.

* Free software: `MIT license <https://github.com/Querela/python-krakenexapi/blob/master/LICENSE>`_

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
