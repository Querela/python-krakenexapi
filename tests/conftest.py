import string
from base64 import b64encode
from random import choices

import pytest


@pytest.fixture(scope="session")
def api_public():
    """BasicKrakenExAPI instance for shared call rate limiting."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()

    return api


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
def api_fake(api_fake_keyfile):
    """Faked `BasicKrakenExAPI` instance with fake key loaded. Should be used
    for mocking requests."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()
    api.load_key(api_fake_keyfile)

    return api
