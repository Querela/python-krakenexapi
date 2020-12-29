# import pytest

# from krakenexapi.api import BasicKrakenExAPIPrivateUserDataMethods
# from krakenexapi.api import BasicKrakenExAPI


def test_get_account_balance(mocker, api_fake):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_private")

    mockquery.return_value = {"ZEUR": 1.0, "ZUSD": 2.0, "XXBT": 3.0, "XTZ.S": 0.4}
    assert api_fake.get_account_balance() == mockquery.return_value
    mockquery.assert_called_once()


def test_get_trade_balance(mocker, api_fake):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_private")

    mockquery.return_value = {
        "eb": 2.2345,
        "tb": 1.1234,
        "m": 0.0,
        "n": 0.0,
        "c": 0.0,
        "v": 0.0,
        "e": 1.1234,
        "mf": 1.1234,
    }
    assert api_fake.get_trade_balance() == mockquery.return_value
    mockquery.assert_called_once()


def test_get_trade_volume(mocker, api_fake):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_private")

    ret_base = {"currency": "ZUSD", "volume": "12.1234"}
    ret_pair = {
        **ret_base,
        "fees": {
            "XXBTZEUR": {
                "fee": "0.2600",
                "minfee": "0.1000",
                "maxfee": "0.2600",
                "nextfee": "0.2400",
                "nextvolume": "50000.0000",
                "tiervolume": "0.0000",
            }
        },
        "fees_maker": {
            "XXBTZEUR": {
                "fee": "0.1600",
                "minfee": "0.0000",
                "maxfee": "0.1600",
                "nextfee": "0.1400",
                "nextvolume": "50000.0000",
                "tiervolume": "0.0000",
            }
        },
    }

    ret_base_f = {"currency": "ZUSD", "volume": 12.1234}
    ret_pair_f = {
        **ret_base_f,
        "fees": {
            "XXBTZEUR": {
                "fee": 0.26,
                "minfee": 0.1,
                "maxfee": 0.26,
                "nextfee": 0.24,
                "nextvolume": 50000.0,
                "tiervolume": 0.0,
            }
        },
        "fees_maker": {
            "XXBTZEUR": {
                "fee": 0.16,
                "minfee": 0.0,
                "maxfee": 0.16,
                "nextfee": 0.14,
                "nextvolume": 50000.0,
                "tiervolume": 0.0,
            }
        },
    }

    mockquery.return_value = ret_base
    assert api_fake.get_trade_volume() == ret_base_f
    mockquery.assert_called_once()
    mockquery.reset_mock()

    mockquery.return_value = ret_pair
    ret = api_fake.get_trade_volume("xxbtzeur")
    assert ret == ret_pair_f
    assert ret_base_f.items() <= ret.items()
    mockquery.assert_called_once()
    mockquery.reset_mock()

    # fee-info without effect?


#
