import datetime

import pytest

# from krakenexapi.api import BasicKrakenExAPIPublicMethods
# from krakenexapi.api import BasicKrakenExAPI


# api_public fixture?
#   will it be mocked if it already exists? - seems to be

# NOTE: here we assume that the api always returns valid responses (no errors
# because of user - those we tested in another file)


def test_get_server_time(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    mockquery.return_value = 1
    assert api_public._get_server_time() == 1
    mockquery.assert_called_once()
    mockquery.reset_mock()

    dt = datetime.datetime.now()
    mockquery.return_value = {"unixtime": dt.timestamp()}  # 'rfc1123': ...
    assert api_public.get_server_time() == dt
    mockquery.assert_called_once()


def test_get_system_status(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    ret = {"status": "online", "timestamp": "2020-05-04T03:02:01Z"}

    mockquery.return_value = ret
    assert api_public.get_system_status() == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()


def test_get_asset_info(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    ret1 = {
        "ZEUR": {
            "aclass": "currency",
            "altname": "EUR",
            "decimals": 4,
            "display_decimals": 2,
        }
    }
    ret2 = {
        "XXBT": {
            "aclass": "currency",
            "altname": "XBT",
            "decimals": 10,
            "display_decimals": 5,
        },
        "ZEUR": {
            "aclass": "currency",
            "altname": "EUR",
            "decimals": 4,
            "display_decimals": 2,
        },
    }
    ret3 = {
        "XETH": {
            "aclass": "currency",
            "altname": "ETH",
            "decimals": 10,
            "display_decimals": 5,
        },
        "XXBT": {
            "aclass": "currency",
            "altname": "XBT",
            "decimals": 10,
            "display_decimals": 5,
        },
        "ZEUR": {
            "aclass": "currency",
            "altname": "EUR",
            "decimals": 4,
            "display_decimals": 2,
        },
    }

    mockquery.return_value = ret1
    assert api_public.get_asset_info("zeur") == ret1
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_info("ZeUr") == ret1
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_info(["ZEUR"]) == ret1
    mockquery.assert_called_once()
    mockquery.reset_mock()

    mockquery.return_value = ret2
    assert api_public.get_asset_info(["ZEUR", "XXBT"]) == ret2
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_info("ZEUR,XXBT") == ret2
    mockquery.assert_called_once()
    mockquery.reset_mock()

    # NOTE: the following is probably a bad test, test with real data?
    mockquery.return_value = ret3
    assert api_public.get_asset_info() == ret3
    mockquery.assert_called_once()


def test_get_asset_pairs(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    ret_orig = {
        "XXBTZEUR": {
            "altname": "XBTEUR",
            "wsname": "XBT/EUR",
            "aclass_base": "currency",
            "base": "XXBT",
            "aclass_quote": "currency",
            "quote": "ZEUR",
            "lot": "unit",
            "pair_decimals": 1,
            "lot_decimals": 8,
            "lot_multiplier": 1,
            "leverage_buy": [2, 3, 4, 5],
            "leverage_sell": [2, 3, 4, 5],
            "fees": [
                [0, 0.26],
                [50000, 0.24],
                [100000, 0.22],
                [250000, 0.2],
                [500000, 0.18],
                [1000000, 0.16],
                [2500000, 0.14],
                [5000000, 0.12],
                [10000000, 0.1],
            ],
            "fees_maker": [
                [0, 0.16],
                [50000, 0.14],
                [100000, 0.12],
                [250000, 0.1],
                [500000, 0.08],
                [1000000, 0.06],
                [2500000, 0.04],
                [5000000, 0.02],
                [10000000, 0],
            ],
            "fee_volume_currency": "ZUSD",
            "margin_call": 80,
            "margin_stop": 40,
            "ordermin": "0.001",
        }
    }
    ret_static = {
        "aclass_base": "currency",
        "aclass_quote": "currency",
        "fee_volume_currency": "ZUSD",
        "lot": "unit",
        "lot_decimals": 8,
        "lot_multiplier": 1,
        "margin_call": 80,
        "margin_stop": 40,
    }
    ret = {
        "XXBTZEUR": {
            "altname": "XBTEUR",
            "wsname": "XBT/EUR",
            "base": "XXBT",
            "quote": "ZEUR",
            "pair_decimals": 1,
            "leverage_buy": [2, 3, 4, 5],
            "leverage_sell": [2, 3, 4, 5],
            "fees": [
                [0, 0.26],
                [50000, 0.24],
                [100000, 0.22],
                [250000, 0.2],
                [500000, 0.18],
                [1000000, 0.16],
                [2500000, 0.14],
                [5000000, 0.12],
                [10000000, 0.1],
            ],
            "fees_maker": [
                [0, 0.16],
                [50000, 0.14],
                [100000, 0.12],
                [250000, 0.1],
                [500000, 0.08],
                [1000000, 0.06],
                [2500000, 0.04],
                [5000000, 0.02],
                [10000000, 0],
            ],
            "ordermin": 0.001,
        }
    }

    # not sure what exactly the test will express (besides coverage ...)
    mockquery.return_value = ret_orig

    assert api_public._get_asset_pairs() == ret_orig
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public._get_asset_pairs_static_values() == ret_static
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_pairs() == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_pairs("xxbtzeur") == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_asset_pairs(["xxbtzeur"]) == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()


def test_get_ticker_information(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    # EQuery:Unknown asset pair

    ret_orig = {
        "XXBTZEUR": {
            "a": ["22129.50000", "1", "1.000"],
            "b": ["22129.40000", "15", "15.000"],
            "c": ["22129.40000", "0.00628513"],
            "v": ["5257.09215204", "5398.22122344"],
            "p": ["22031.25033", "22017.14091"],
            "t": [53706, 55156],
            "l": ["21160.50000", "21160.50000"],
            "h": ["22498.00000", "22498.00000"],
            "o": "21329.80000",
        }
    }
    ret = {
        "XXBTZEUR": {
            "a": [22129.50000, 1, 1.000],
            "b": [22129.40000, 15, 15.000],
            "c": [22129.40000, 0.00628513],
            "v": [5257.09215204, 5398.22122344],
            "p": [22031.25033, 22017.14091],
            "t": [53706, 55156],
            "l": [21160.50000, 21160.50000],
            "h": [22498.00000, 22498.00000],
            "o": 21329.80000,
        }
    }

    with pytest.raises(TypeError):
        api_public.get_ticker_information()

    mockquery.return_value = ret_orig
    assert api_public._get_ticker_information("xxbtzeur") == ret_orig
    mockquery.assert_called_once()
    mockquery.reset_mock()

    assert api_public.get_ticker_information("xxbtzeur") == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()


def test_get_ohlc_data(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    from krakenexapi.api import _OHLCEntry

    ret_orig = {
        "XXBTZEUR": [
            [
                1234567020,
                "22136.9",
                "22136.9",
                "22103.3",
                "22115.4",
                "22124.0",
                "19.32476339",
                74,
            ]
        ],
        "last": 1234567000,
    }
    ret = (
        [
            _OHLCEntry._make(
                [
                    1234567020,
                    22136.9,
                    22136.9,
                    22103.3,
                    22115.4,
                    22124.0,
                    19.32476339,
                    74,
                ]
            )
        ],
        1234567000,
    )

    with pytest.raises(TypeError):
        api_public.get_ohlc_data()

    mockquery.return_value = ret_orig
    assert api_public.get_ohlc_data("xxbtzeur") == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()

    with pytest.raises(AssertionError):
        api_public.get_ohlc_data("xxbtzeur", interval=3)
    mockquery.assert_not_called()


def test_get_order_book(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    from krakenexapi.api import _OrderBookEntry

    ret_orig = {
        "XXBTZEUR": {
            "asks": [["22174.10000", "6.388", 1234568702]],
            "bids": [["22174.00000", "1.524", 1234568701]],
        }
    }
    ret = (
        [_OrderBookEntry._make([22174.10000, 6.388, 1234568702])],
        [_OrderBookEntry._make([22174.00000, 1.524, 1234568701])],
    )

    with pytest.raises(TypeError):
        api_public.get_order_book()

    mockquery.return_value = ret_orig
    assert api_public.get_order_book("xxbtzeur", 1) == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()


def test_get_recent_trades(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    from krakenexapi.api import _RecentTradeEntry

    ret_orig = {
        "XXBTZEUR": [
            ["22142.20000", "0.00101974", 1111111571.7057, "b", "l", ""],
            ["22139.30000", "0.03589640", 1111111580.9614, "b", "m", ""],
            ["22139.20000", "0.02921670", 1111111586.3467, "b", "m", ""],
        ],
        "last": "1111111222222210315",
    }
    ret = (
        [
            _RecentTradeEntry._make(
                [22142.20000, 0.00101974, 1111111571.7057, "b", "l", None]
            ),
            _RecentTradeEntry._make(
                [22139.30000, 0.03589640, 1111111580.9614, "b", "m", None]
            ),
            _RecentTradeEntry._make(
                [22139.20000, 0.02921670, 1111111586.3467, "b", "m", None]
            ),
        ],
        "1111111222222210315",
    )

    with pytest.raises(TypeError):
        api_public.get_recent_trades()

    mockquery.return_value = ret_orig
    assert api_public.get_recent_trades("xxbtzeur") == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()


def test_get_recent_spread_data(mocker, api_public):
    mockquery = mocker.patch("krakenexapi.api.RawKrakenExAPI.query_public")

    from krakenexapi.api import _RecentSpreadEntry

    ret_orig = {
        "XXBTZEUR": [[1609200111, "22053.50000", "22054.10000"]],
        "last": 1609200111,
    }
    ret = (
        [_RecentSpreadEntry._make([1609200111, 22053.50000, 22054.10000])],
        1609200111,
    )

    with pytest.raises(TypeError):
        api_public.get_recent_spread_data()

    mockquery.return_value = ret_orig
    assert api_public.get_recent_spread_data("xxbtzeur") == ret
    mockquery.assert_called_once()
    mockquery.reset_mock()
