import datetime

import pytest

pytestmark = [pytest.mark.liveapi, pytest.mark.apipublic]


def test_get_server_time(api_public):
    st_raw = api_public._get_server_time()
    assert isinstance(st_raw, dict)
    assert "unixtime" in st_raw
    assert "rfc1123" in st_raw

    st = api_public.get_server_time()
    assert isinstance(st, datetime.datetime)
    now = datetime.datetime.now()
    diff = abs(now - st)
    assert diff.total_seconds() <= 2 * 24 * 60 * 60


# NOTE: guard against missing markers in fixture
# def test_missing_marker(api_private):
#     pytest.fail("this should never be reached!?")
