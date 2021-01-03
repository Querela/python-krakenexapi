import pytest

# pytestmark = [pytest.mark.liveapi, pytest.mark.apiprivate]


def test_ok():
    pass


@pytest.mark.liveapi
def test_l():
    pass


@pytest.mark.liveapi
@pytest.mark.apiprivate
def test_lpr():
    pass


@pytest.mark.liveapi
@pytest.mark.apipublic
def test_lpu():
    pass


@pytest.mark.liveapi
@pytest.mark.apiprivate
@pytest.mark.apipublic
def test_lprpu():
    pass


@pytest.mark.apiprivate
@pytest.mark.apipublic
def test_prpu():
    pass


@pytest.mark.apiprivate
def test_pr():
    pass


@pytest.mark.apipublic
def test_pu():
    pass
