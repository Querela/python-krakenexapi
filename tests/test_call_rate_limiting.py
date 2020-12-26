import time

import pytest

from krakenexapi.api import _CallRateLimitInfo


def test_crli_exact():
    crl = _CallRateLimitInfo(limit=10, cost=5, decay=2)
    assert crl._counter == 0.0
    assert crl.can_call(cost=0)
    assert crl.time_to_call(cost=0) == 0.0

    crl._counter = crl._limit
    assert crl.can_call(cost=0)
    assert not crl.can_call(cost=None)

    crl._counter = crl._limit + 0.00001
    assert not crl.can_call(cost=0)
    assert crl.time_to_call(cost=0) == pytest.approx(0.00001 / crl._decay)

    crl._counter = crl._limit - crl._cost
    assert crl.can_call(cost=0)
    assert crl.can_call(cost=None)
    assert crl.can_call()

    crl._counter = crl._limit + 1 * crl._cost
    assert crl.time_to_call(0) == crl._cost / crl._decay
    assert crl.time_to_call(crl._cost) == 2 * crl._cost / crl._decay

    crl._counter = crl._limit + 2.5 * crl._decay
    assert crl.time_to_call(0) == 2.5


def test_crli_1per1():
    crl = _CallRateLimitInfo(limit=1, cost=1, decay=1)
    assert crl.can_call()
    assert crl.check()
    assert 0 <= crl._counter <= crl._limit
    assert not crl.check()
    assert not crl.can_call()

    seconds = crl.time_to_call(crl._cost)
    assert seconds >= 0.0
    time.sleep(seconds)
    assert crl.check()

    crl.check_and_wait()
    assert not crl.check()
    crl.check_and_wait()
    assert not crl.check()


def test_crli_nperm():
    crl = _CallRateLimitInfo(limit=10, cost=5, decay=2.5)
    assert crl.check()
    assert crl.check()
    assert not crl.check()
    crl.check_and_wait()
    assert not crl.check()

    seconds = crl.time_to_call(crl._cost)
    assert seconds >= 0.0
    time.sleep(seconds)
    assert crl.check()
