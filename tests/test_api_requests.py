import pytest

from krakenexapi.api import RawKrakenExAPI
from krakenexapi.exceptions import KrakenExAPIError
from krakenexapi.exceptions import NoPrivateKey
from krakenexapi.exceptions import NoSuchAPIMethod


def test_query_raw_normal(mocker):
    mocksesscls = mocker.patch("requests.Session")
    mocksess = mocksesscls.return_value
    mockresp = mocksess.post.return_value
    mockresp.json.return_value = {"result": {"k": "123"}}

    api = RawKrakenExAPI()
    assert mocksesscls.called
    assert api.session == mocksess
    ret = api._query_raw("/0/public/Test", data=dict(a=1), headers=dict(h=2))
    mocksess.post.assert_called_once_with(
        f"{api.api_domain}/0/public/Test",
        data=dict(a=1),
        headers=dict(h=2),
        timeout=None,
    )

    assert ret == {"k": "123"}


def test_query_raw_error(mocker):
    mocksesscls = mocker.patch("requests.Session")
    mocksess = mocksesscls.return_value
    mockresp = mocksess.post.return_value
    mockresp.json.return_value = {"error": ["XMsg", "XMsg3"]}

    api = RawKrakenExAPI()
    assert mocksesscls.called
    assert api.session == mocksess
    with pytest.raises(KrakenExAPIError) as exc_info:
        api._query_raw("/0/public/Test", data=dict(), headers=dict())
    assert "XMsg, XMsg3" in str(exc_info.value)
    mocksess.post.assert_called_once_with(
        f"{api.api_domain}/0/public/Test", data=dict(), headers=dict(), timeout=None
    )


def test_query_public(mocker):
    mocksess = mocker.patch("requests.Session").return_value
    mockresp = mocksess.post.return_value
    mockresp.json.return_value = {"result": {"k": "123"}}

    api = RawKrakenExAPI()

    with pytest.raises(KrakenExAPIError) as exc_info:
        ret = api.query_public("Test", **dict(b=5))
    assert type(exc_info.value) == NoSuchAPIMethod
    mocksess.post.assert_not_called()

    ret = api.query_public("Time", **dict(b=5))
    mocksess.post.assert_called_once_with(
        f"{api.api_domain}/0/public/Time", data=dict(b=5), headers=dict(), timeout=None
    )
    assert ret == {"k": "123"}


def test_query_public2(mocker):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI._query_raw")
    mockquery.return_value = {"k": "123"}

    api = RawKrakenExAPI()

    with pytest.raises(KrakenExAPIError) as exc_info:
        ret = api.query_public("Test", **dict(b=5))
    assert type(exc_info.value) == NoSuchAPIMethod
    mockquery.assert_not_called()

    ret = api.query_public("Time", **dict(b=5))
    mockquery.assert_called_once_with("/0/public/Time", data=dict(b=5), headers=dict())
    assert ret == {"k": "123"}


def test_query_private_invalid_method(mocker):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI._query_raw")
    mockquery.return_value = {"k": "123"}

    api = RawKrakenExAPI()

    with pytest.raises(KrakenExAPIError) as exc_info:
        api.query_private("Time", **dict(b=5))
    assert type(exc_info.value) == NoSuchAPIMethod
    mockquery.assert_not_called()


def test_query_private_no_key(mocker):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI._query_raw")
    mockquery.return_value = {"k": "123"}

    api = RawKrakenExAPI()

    with pytest.raises(KrakenExAPIError) as exc_info:
        api.query_private("Balance", **dict(b=5))
    assert type(exc_info.value) == NoPrivateKey
    mockquery.assert_not_called()


def test_query_private_ok_fake(mocker, api_fake_key, api_fake_secret):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI._query_raw")
    mocksign = mocker.patch("krakenexapi.api.RawKrakenExAPI._sign")
    mockquery.return_value = {"k": "123"}
    mocksign.return_value = "sign"

    api = RawKrakenExAPI(key=api_fake_key, secret=api_fake_secret)

    ret = api.query_private("Balance", **dict(b=5))
    mockquery.assert_called_once()
    mocksign.assert_called_once()
    cargs, ckwargs = mockquery.call_args
    assert cargs[0] == "/0/private/Balance"
    assert ("b", 5) in ckwargs["data"].items()
    assert "nonce" in ckwargs["data"]
    assert ckwargs["headers"] == {
        "API-Key": api_fake_key,
        "API-Sign": mocksign.return_value,
    }
    cargs, _ = mocksign.call_args
    assert cargs[0] == "/0/private/Balance"
    assert ("b", 5) in cargs[1].items()
    assert "nonce" in cargs[1]
    assert ret == {"k": "123"}


#
