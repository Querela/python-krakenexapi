import pytest

from krakenexapi.wallet import Asset
from krakenexapi.wallet import CryptoSellTransaction
from krakenexapi.wallet import Currency

pytestmark = [pytest.mark.liveapi, pytest.mark.apiprivate]


def test_asset_cost_price(api_private):
    asset = Asset(Currency.find("xxbt"), api_private, Currency.find("zeur"))

    # vol * price == cost
    # vol == cost / price
    vol_buy = asset.cost_buy / asset.price_buy_avg
    vol_sell = asset.cost_sell / asset.price_sell_avg

    assert (vol_buy - vol_sell) == asset.amount_by_transactions

    vol_transactions = sum(
        [
            (-1 if isinstance(t, CryptoSellTransaction) else +1) * t.amount
            for t in asset._Asset__transactions
        ]
    )
    assert vol_transactions == asset.amount_by_transactions


def test_asset_amounts(api_private):
    cur_base = Currency.find("xxbt")
    cur_quote = Currency.find("zeur")
    asset = Asset(cur_base, api_private, cur_quote)

    # we should not have too much loss
    # NOTE: transfers might skew the difference
    pytest.approx(asset.amount, asset.amount_by_transactions, 0.00001)


@pytest.mark.xfail(reason="difference in amounts")
def test_asset_amounts_exact(api_private):
    cur_base = Currency.find("xxbt")
    cur_quote = Currency.find("zeur")
    asset = Asset(cur_base, api_private, cur_quote)

    assert cur_base.round_value(asset.amount) == cur_base.round_value(
        asset.amount_by_transactions
    )


def test_asset_noloss_price(api_private):
    cur_base = Currency.find("xxbt")
    cur_quote = Currency.find("zeur")
    asset = Asset(cur_base, api_private, cur_quote)

    cost_sell_noloss = asset.price_for_noloss() * asset.amount
    pytest.approx(cost_sell_noloss, asset.cost, 10)

    pytest.approx(asset.price_for_noloss() * asset.amount, asset.cost, 10)


@pytest.mark.xfail(reason="noloss price not exact enough")
def test_asset_noloss_price_exact(api_private):
    cur_base = Currency.find("xxbt")
    cur_quote = Currency.find("zeur")
    asset = Asset(cur_base, api_private, cur_quote)

    # should raise
    assert asset.price_for_noloss() * asset.amount == asset.cost
