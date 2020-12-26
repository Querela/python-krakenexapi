import pytest


@pytest.fixture(scope="session")
def api_public():
    """BasicKrakenExAPI instance for shared call rate limiting."""
    from krakenexapi.api import BasicKrakenExAPI

    api = BasicKrakenExAPI()

    return api
