
Changelog
=========

WIP
---

* Add tests (raw query, public + private API).
* Add tooling for docs, checks.
* Add meta info dataclasses...
* Fix many minor issues, badges, docs, workflows/tests.
* Add wrappers around transactions, handling, statistics etc.
* Rename private user data ledgers endpoints!
* Extract exceptions into own module.
* Start with websocket API.
* Add live-api tests (markers, github workflow).
* Call rate limiting - retry with backoff.
* Add Funds (same as Assets) to ``wallet.py``.
* Rewrite ``wallet.py``, group functions, add :class:`~krakenexapi.wallet.Wallet`.

0.0.1 (2020-12-27)
------------------

* Add raw kraken Exchange API.
* Add basic Kraken Exchange API - public methods.
* Add custom exceptions.
* Add basic response classes for better accessing of entries, fix stringified floats.
* Add call rate limiting (crl).
* Add tests for crl, more in work.
* Add private user data API endpoints.
* Add basic documentation.
* First official pre-release.

0.0.0 (2020-12-25)
------------------

* First release on PyPI.
