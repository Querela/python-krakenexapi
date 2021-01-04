import string
from base64 import b64encode
from random import choices

import pytest

# ----------------------------------------------------------------------------


def pytest_addoption(parser):
    parser.addoption(
        "--live-api",
        action="store_true",
        help="run the tests with live API requests (marked with 'liveapi')",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "liveapi: mark test to execute real API requests"
    )
    config.addinivalue_line(
        "markers", "apiprivate: mark test to run private API method tests"
    )
    config.addinivalue_line(
        "markers", "apipublic: mark test to run public API method tests"
    )


def pytest_collection_modifyitems(config, items):
    # for item in items:
    #     if "apiprivate" in item.keywords:
    #         item.add_marker(pytest.mark.liveapi)
    #     if "apipublic" in item.keywords:
    #         item.add_marker(pytest.mark.liveapi)

    if config.getoption("--live-api"):
        # --live-api given in cli: do not skip live API request tests
        return

    skip_liveapi = pytest.mark.skip(reason="need '--live-api' option to run")
    for item in items:
        if "liveapi" in item.keywords:
            item.add_marker(skip_liveapi)


# NOTE: for print output specify: -rA


def pytest_runtest_setup(item):
    # print(item)
    # print(list(item.keywords))
    # print([m.name for m in item.own_markers])
    # print(item.config.option.markexpr)
    # print(Expression.compile(item.config.option.markexpr))
    pass


# ----------------------------------------------------------------------------


# NOTE: marker fixtures for development, to guard against missing annotations


@pytest.fixture(scope="function")
def _marker_liveapi(request):
    """Guarded against missing marker: liveapi."""
    # NOTE: only works in function scope
    # so, wrapping required if session scoped
    marker = request.node.get_closest_marker("liveapi")
    if marker is None:
        request.raiseerror("requires 'liveapi' marker on test")

    return None


@pytest.fixture(scope="function")
def _marker_apipublic(request):
    """Guarded against missing marker: apipublic."""
    marker = request.node.get_closest_marker("apipublic")
    if marker is None:
        request.raiseerror("requires 'apipublic' marker on test")

    return None


@pytest.fixture(scope="function")
def _marker_apiprivate(request):
    """Guarded against missing marker: apiprivate."""
    marker = request.node.get_closest_marker("apiprivate")
    if marker is None:
        request.raiseerror("requires 'apiprivate' marker on test")

    return None


@pytest.fixture(scope="session")
def api_public():
    """BasicKrakenExAPI instance for shared call rate limiting."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()

    return api


# @pytest.fixture(scope="function")
# def api_public(_marker_liveapi, _marker_apipublic, _api_public):
#     """BasicKrakenExAPI instance for shared call rate limiting.
#
#     Guarded against missing markers. Wraps session-scoped `_api_public`.
#     """
#     return _api_public


@pytest.fixture(scope="session")
def _api_private():
    """BasicKrakenExAPI instance for private API requests and shared call rate limiting."""
    from krakenexapi.api import BasicKrakenExAPI
    from krakenexapi.wallet import CurrencyPair

    api = BasicKrakenExAPI()
    api.load_key()

    print("load currency pairs ...")
    CurrencyPair.build_from_api(api)

    return api


@pytest.fixture(scope="function")
def api_private(_marker_liveapi, _marker_apiprivate, _api_private):
    """BasicKrakenExAPI instance for private API requests and shared call rate limiting.

    Guarded against missing markers. Wraps session-scoped `_api_private`.
    """
    return _api_private


@pytest.fixture(scope="function")
def api_fake_key():
    """Fake API key"""

    rnds = choices(string.ascii_uppercase + string.digits, k=10)
    key = f"key-{rnds}"
    key = key.encode("utf-8")
    key = b64encode(key)
    key = key.decode("utf-8")

    return key


@pytest.fixture(scope="function")
def api_fake_secret():
    """Fake API secret"""

    rnds = choices(string.ascii_uppercase + string.digits, k=10)
    secret = f"secret-{rnds}"
    secret = secret.encode("utf-8")
    secret = b64encode(secret)
    secret = secret.decode("utf-8")

    return secret


@pytest.fixture(scope="function")
def api_fake_keyfile(tmp_path, api_fake_key, api_fake_secret):
    """Fake API *kraken.key* file (with key & secret)"""
    fake_kraken_key_file = tmp_path / "kraken.key"
    fake_kraken_key_file.write_text(
        f"key = {api_fake_key}\n" f"secret = {api_fake_secret}\n"
    )
    return fake_kraken_key_file


@pytest.fixture(scope="function")
def api_public_fake(monkeypatch):
    """Faked `BasicKrakenExAPI` instance without fake key loaded. Should be used
    for mocking public requests."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()
    monkeypatch.delattr(api, "session")
    monkeypatch.delattr("requests.sessions.Session.request")

    return api


@pytest.fixture(scope="function")
def api_fake(api_fake_keyfile, monkeypatch):
    """Faked `BasicKrakenExAPI` instance with fake key loaded. Should be used
    for mocking requests."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()
    monkeypatch.delattr(api, "session")
    monkeypatch.delattr("requests.sessions.Session.request")

    api.load_key(api_fake_keyfile)

    return api


# ----------------------------------------------------------------------------
