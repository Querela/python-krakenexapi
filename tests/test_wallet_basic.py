import pytest

from krakenexapi.wallet import Currency
from krakenexapi.wallet import CurrencyPair

FAKE_CURENCY_RESPONSE = {
    "XZEC": {
        "aclass": "currency",
        "altname": "ZEC",
        "decimals": 10,
        "display_decimals": 5,
    },
    "ZEUR": {
        "aclass": "currency",
        "altname": "EUR",
        "decimals": 4,
        "display_decimals": 2,
    },
    "XTZ.S": {
        "aclass": "currency",
        "altname": "XTZ.S",
        "decimals": 8,
        "display_decimals": 6,
    },
}
FAKE_CURENCYPAIR_RESPONSE = {
    "XZECZEUR": {
        "altname": "ZECEUR",
        "wsname": "ZEC/EUR",
        "base": "XZEC",
        "quote": "ZEUR",
        "pair_decimals": 3,
        "leverage_buy": [2],
        "leverage_sell": [2],
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
        "ordermin": 0.03,
    }
}


def test_currency_properties(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)

    c1 = Currency("Sym", "Nam", 2, 1)
    assert c1.symbol == "Sym"
    assert not c1.is_fiat
    assert not c1.is_staked
    assert Currency.all_symbols() == {"SYM"}
    assert Currency.all_symbols(unique=False) == {"SYM", "NAM"}

    c2 = Currency("ZEUR", "EUR", 8, 3)
    assert c2.symbol == "ZEUR"
    assert c2.is_fiat
    assert not c2.is_staked

    c3 = Currency("ZEUR.M", "eur.m", 8, 3)
    assert c3.symbol == "ZEUR.M"
    assert c3.is_fiat
    assert c3.is_staked
    assert c3.is_staked_offchain

    c4 = Currency("XTZ.S", "xtz.s", 8, 3)
    assert c4.symbol == "XTZ.S"
    assert not c4.is_fiat
    assert c4.is_staked
    assert c4.is_staked_onchain


def test_currency_singleton(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)

    assert Currency.all_symbols() == set()

    c1 = Currency("Sym", "Nam", 2, 1)
    assert Currency.all_symbols() == {"SYM"}
    assert Currency.all_symbols(unique=False) == {"SYM", "NAM"}

    _ = Currency("ZSYM2", "ZSym2", 2, 1)
    assert Currency.all_symbols(unique=False) == {"SYM", "NAM", "ZSYM2"}

    with pytest.raises(AssertionError):
        Currency("Sym", "Nam3", 3, 2)

    cx = Currency.find("sym")
    assert id(cx) == id(c1)

    cx2 = Currency.find("nam")
    assert id(cx) == id(cx2)

    with pytest.raises(KeyError):
        Currency.find("sym3")


def test_currency_from_fakeapi_empty(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)

    attrs = {"get_asset_info.return_value": {}}
    fakeapi = mocker.Mock(**attrs)

    Currency.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()

    assert Currency.all_symbols() == set()


def test_currency_from_fakeapi_two_currencies(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)

    attrs = {"get_asset_info.return_value": FAKE_CURENCY_RESPONSE}
    fakeapi = mocker.Mock(**attrs)

    Currency.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()

    assert Currency.all_symbols() == {"XZEC", "ZEUR", "XTZ.S"}
    assert Currency.all_symbols(unique=False) == {"XZEC", "ZEUR", "XTZ.S"} | {
        "ZEC",
        "EUR",
        "XTZ.S",
    }


def test_currencypair_properties(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)
    mocker.patch.dict(CurrencyPair._CurrencyPair__currency_pairs, dict(), clear=True)

    assert CurrencyPair.all_symbols() == set()

    c1 = Currency("Sym", "Nam", 2, 1)
    c2 = Currency("Sym2", "Nam2", 2, 1)
    c3 = Currency("ZSYM3", "Nam3", 2, 1)
    assert Currency.all_symbols() == {"SYM", "SYM2", "ZSYM3"}
    assert Currency.all_symbols(unique=False) == {"SYM", "SYM2", "ZSYM3"} | {
        "NAM",
        "NAM2",
        "NAM3",
    }
    assert not c1.is_fiat
    assert not c2.is_fiat
    assert c3.is_fiat

    cpcf1 = CurrencyPair("S1", "SS", "S/S", 1, c1, c3, 0.01)
    cpcf2 = CurrencyPair("S2", "S2S", "S2/S", 6, c2, c3, 100)
    cpcc = CurrencyPair("S3", "S3S", "S3/S", 6, c1, c2, 100)
    cpff = CurrencyPair("S4", "S4S", "S4/S", 6, c3, c3, 100)
    assert CurrencyPair.all_symbols() == {"S1", "S2", "S3", "S4"}
    assert CurrencyPair.all_symbols(unique=False) == {"S1", "S2", "S3", "S4"} | {
        "SS",
        "S2S",
        "S3S",
        "S4S",
    }

    assert cpcf1.is_fiat2crypto
    assert cpcf2.is_fiat2crypto
    assert cpcc.is_crypto2crypto
    assert cpff.is_fiat2fiat


def test_currencypair_singleton(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)
    mocker.patch.dict(CurrencyPair._CurrencyPair__currency_pairs, dict(), clear=True)

    assert CurrencyPair.all_symbols() == set()

    c1 = Currency("Sym", "Sym", 2, 1)
    c2 = Currency("Sym2", "Sym2", 2, 1)
    c3 = Currency("ZSYM3", "ZSym3", 2, 1)
    assert Currency.all_symbols() == {"SYM", "SYM2", "ZSYM3"}

    cp1 = CurrencyPair("SYMZSYM3", "SS", "S/S", 1, c1, c3, 0.01)
    cp2 = CurrencyPair("SYM2ZSYM3", "S2S", "S2/S", 6, c2, c3, 100)
    assert CurrencyPair.all_symbols() == {"SYMZSYM3", "SYM2ZSYM3"}
    assert CurrencyPair.all_symbols(unique=False) == {"SYMZSYM3", "SYM2ZSYM3"} | {
        "SS",
        "S2S",
    }

    with pytest.raises(AssertionError):
        CurrencyPair("SYMZSYM3", "SSx", "S/Sx", 1, c1, c3, 0.01)

    assert cp1 != cp2

    cpx = CurrencyPair.find("symzsym3")
    assert id(cpx) == id(cp1)

    cpx2 = CurrencyPair.find("ss")
    assert id(cpx) == id(cpx2)

    with pytest.raises(KeyError):
        CurrencyPair.find("sym3")

    with pytest.raises(KeyError):
        CurrencyPair.find("SYM3ZSYM3")


def test_currencypair_from_fakeapi_empty(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)
    mocker.patch.dict(CurrencyPair._CurrencyPair__currency_pairs, dict(), clear=True)

    attrs = {"get_asset_info.return_value": {}, "get_asset_pairs.return_value": {}}
    fakeapi = mocker.Mock(**attrs)

    Currency.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()
    fakeapi.get_asset_info.reset_mock()

    CurrencyPair.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()
    fakeapi.get_asset_pairs.assert_called_once_with()

    assert Currency.all_symbols() == set()
    assert CurrencyPair.all_symbols() == set()


def test_currencypair_from_fakeapi_missing_currency(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)
    mocker.patch.dict(CurrencyPair._CurrencyPair__currency_pairs, dict(), clear=True)

    attrs = {
        "get_asset_info.return_value": {},
        "get_asset_pairs.return_value": FAKE_CURENCYPAIR_RESPONSE,
    }
    fakeapi = mocker.Mock(**attrs)

    with pytest.raises(KeyError):
        CurrencyPair.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()
    fakeapi.get_asset_pairs.assert_called_once_with()

    assert Currency.all_symbols() == set()
    assert CurrencyPair.all_symbols() == set()


def test_currencypair_from_fakeapi(mocker):
    mocker.patch.dict(Currency._Currency__currencies, dict(), clear=True)
    mocker.patch.dict(CurrencyPair._CurrencyPair__currency_pairs, dict(), clear=True)

    attrs = {
        "get_asset_info.return_value": FAKE_CURENCY_RESPONSE,
        "get_asset_pairs.return_value": FAKE_CURENCYPAIR_RESPONSE,
    }
    fakeapi = mocker.Mock(**attrs)
    Currency.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()

    CurrencyPair.build_from_api(fakeapi)
    fakeapi.get_asset_info.assert_called_once_with()
    fakeapi.get_asset_pairs.assert_called_once_with()

    assert Currency.all_symbols(unique=False) == {"XZEC", "ZEUR", "XTZ.S"} | {
        "ZEC",
        "EUR",
    }
    assert CurrencyPair.all_symbols(unique=False) == {"XZECZEUR"} | {"ZECEUR"}
    cb = Currency.find("XZEC")
    cq = Currency.find("ZEUR")
    cpr = CurrencyPair.find("XZECZEUR")
    assert cb != cq
    assert cpr.base == cb
    assert cpr.quote == cq


#
