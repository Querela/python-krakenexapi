from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from .api import BasicKrakenExAPIPrivateUserDataMethods
from .api import BasicKrakenExAPIPublicMethods

# ----------------------------------------------------------------------------


# see:
# - https://support.kraken.com/hc/en-us/articles/202944246-All-available-currencies-and-trading-pairs-on-Kraken
# - https://support.kraken.com/hc/en-us/articles/360000678446-Cryptocurrencies-available-on-Kraken
# - https://support.kraken.com/hc/en-us/articles/360039879471-What-is-Asset-S-and-Asset-M-


@dataclass
class Currency:
    symbol: str
    name: str
    decimals: int
    display_decimals: int

    __currencies: ClassVar[Dict[str, "Currency"]] = dict()

    def __post_init__(self):
        symbol = self.symbol.upper()
        assert symbol not in self.__class__.__currencies
        self.__class__.__currencies[symbol] = self

    # --------------------------------

    @property
    def is_fiat(self) -> bool:
        return self.symbol[0].upper() == "Z"

    @property
    def is_staked_onchain(self) -> bool:
        """On-chain staked currency.

        Returns
        -------
        bool
        """
        return self.symbol.endswith(".S")

    @property
    def is_staked_offchain(self) -> bool:
        """Off-chain staked currency.

        Returns
        -------
        bool
        """
        return self.symbol.endswith(".M")

    @property
    def is_staked(self) -> bool:
        return self.is_staked_onchain or self.is_staked_offchain

    # --------------------------------

    def format_value(self, value: float) -> str:
        return f"{value:.{self.display_decimals}f}"

    def round_value(self, value: float) -> float:
        return round(value, self.decimals)

    # --------------------------------

    @classmethod
    def find(cls, symbol: str) -> "Currency":
        return cls.__currencies[symbol.upper()]

    @classmethod
    def all_symbols(cls) -> Set[str]:
        return set(cls.__currencies.keys())

    # --------------------------------

    @classmethod
    def build_from_api(cls, api: BasicKrakenExAPIPublicMethods):
        data = api.get_asset_info()
        for symbol, info in data.items():
            _ = cls(
                symbol=symbol,
                name=info["altname"],
                decimals=info["decimals"],
                display_decimals=info["display_decimals"],
            )

    # --------------------------------


@dataclass
class CurrencyPair:
    symbol: str
    altname: str
    name: str
    pair_decimals: int
    base: Currency
    quote: Currency
    ordermin: Optional[float] = None

    __currency_pairs: ClassVar[Dict[str, "CurrencyPair"]] = dict()

    def __post_init__(self):
        symbol = self.symbol.upper()
        assert symbol not in self.__class__.__currency_pairs
        self.__class__.__currency_pairs[symbol] = self

    # --------------------------------

    @property
    def is_fiat2crypto(self) -> bool:
        return not self.base.is_fiat and self.quote.is_fiat

    @property
    def is_crypto2crypto(self) -> bool:
        return not self.base.is_fiat and not self.quote.is_fiat

    @property
    def is_fiat2fiat(self) -> bool:
        return self.base.is_fiat and self.quote.is_fiat

    # --------------------------------

    @classmethod
    def find(cls, symbol: str) -> "CurrencyPair":
        return cls.__currency_pairs[symbol.upper()]

    @classmethod
    def all_symbols(cls) -> Set[str]:
        return set(cls.__currency_pairs.keys())

    # --------------------------------

    @classmethod
    def build_from_api(cls, api: BasicKrakenExAPIPublicMethods):
        # TODO: check if currencies preloaded!
        if not Currency.all_symbols():
            Currency.build_from_api(api)

        pairs = api.get_asset_pairs()
        for symbol, info in pairs.items():
            base_cur = Currency.find(info["base"])
            quote_cur = Currency.find(info["quote"])
            _ = cls(
                symbol=symbol,
                altname=info["altname"],
                name=info.get("wsname", info["altname"]),
                base=base_cur,
                quote=quote_cur,
                ordermin=info.get("ordermin", None),
                pair_decimals=info["pair_decimals"],
            )

    # --------------------------------


# ----------------------------------------------------------------------------


@dataclass
class TradingTransaction:
    currency_pair: CurrencyPair
    price: float
    amount: float
    cost: float
    fees: float
    # orders / transactions / ledgers
    timestamp: datetime
    txid: str
    otxid: Optional[Union[float, str]] = None

    @property
    def base_currency(self) -> Currency:
        return self.currency_pair.base

    @property
    def quote_currency(self) -> Currency:
        return self.currency_pair.quote


class CryptoBuyTransaction(TradingTransaction):
    pass


class CryptoSellTransaction(TradingTransaction):
    pass


@dataclass
class FundingTransaction:
    currency: Currency
    amount: float
    # ledgers
    timestamp: datetime
    fees: float = 0.0
    lxid: Optional[Union[float, int, str]] = None


class DepositTransaction(FundingTransaction):
    pass


class WithdrawalTransaction(FundingTransaction):
    pass


# ------------------------------------


def build_trading_transactions(
    api: BasicKrakenExAPIPrivateUserDataMethods,
    start: Optional[Union[int, float, str]] = None,
) -> List[TradingTransaction]:
    # query all entries
    trade_entries = dict()
    offset, total = 0, 1
    while offset < total:
        entries, total = api.get_trades_history(start=start, offset=offset)
        if not entries:
            break
        trade_entries.update(entries)
        offset += len(entries)

    # wrap/convert
    transactions = list()
    for txid, info in trade_entries.items():
        params = {
            "currency_pair": CurrencyPair.find(info["pair"]),
            "price": info["price"],
            "amount": info["vol"],
            "cost": info["cost"],
            "fees": info["fee"],
            "timestamp": datetime.fromtimestamp(info["time"]),
            "txid": txid,
            "otxid": info["ordertxid"],
        }
        if info["type"] == "buy":
            tx: TradingTransaction = CryptoBuyTransaction(**params)
        elif info["type"] == "sell":
            tx = CryptoSellTransaction(**params)
        else:
            raise RuntimeError(f"Unknoen transaction type: {info['type']}")
        transactions.append(tx)

    return transactions


def build_funding_transactions(
    api: BasicKrakenExAPIPrivateUserDataMethods,
    start: Optional[Union[int, float, str]] = None,
) -> List[FundingTransaction]:
    # query all entries
    funding_entries = dict()
    offset, total = 0, 1
    while offset < total:
        entries, total = api.get_ledgers_info(
            type="deposit", start=start, offset=offset
        )
        # NOTE: reports incorrect total (not subset count if type filtering)
        if not entries:
            break
        funding_entries.update(entries)
        offset += len(entries)

    offset, total = 0, 1
    while offset < total:
        entries, total = api.get_ledgers_info(
            type="withdrawal", start=start, offset=offset
        )
        if not entries:
            break
        funding_entries.update(entries)
        offset += len(entries)

    # wrap/convert
    transactions = list()
    for lxid, info in funding_entries.items():
        if info["type"] == "transfer":
            # 'type': 'transfer', 'subtype': 'stakingfromspot'
            # XTZ -> XTZ.S
            continue

        params = {
            "currency": Currency.find(info["asset"]),
            "amount": info["amount"],
            "fees": info["fee"],
            "timestamp": datetime.fromtimestamp(info["time"]),
            "lxid": lxid,
        }
        if info["type"] == "deposit":
            tx: FundingTransaction = DepositTransaction(**params)
        elif info["type"] == "withdrawal":
            tx = WithdrawalTransaction(**params)
        else:
            raise RuntimeError(f"Unknoen transaction type: {info['type']}")
        transactions.append(tx)

    return transactions


# ----------------------------------------------------------------------------

# basic assumptions
# - no margin / leverage
# - dead simple - fiat<->crypto trading only
# - aka spot-trading


class Asset:
    def __init__(
        self,
        currency: Currency,
        api: BasicKrakenExAPIPrivateUserDataMethods,
        quote_currency: Optional[Currency] = None,
    ):
        self.__currency = currency
        self.__quote_currency = quote_currency
        self.__amount: float = 0.0
        self.__transactions: List[TradingTransaction] = list()
        self.__last_txid: Optional[Union[int, str]] = None
        self.__api = api

        self._update()

    # --------------------------------

    def _update(self):
        # query ledgers from api
        # - use + update last id
        raise NotImplementedError

    # --------------------------------

    @property
    def currency(self) -> Currency:
        return self.__currency

    @property
    def amount(self) -> float:
        return self.__amount

    # --------------------------------

    @property
    def price_buy_avg(self) -> float:
        pass

    @property
    def price_sell_avg(self) -> float:
        pass

    @property
    def price_for_noloss(self) -> float:
        pass

    @property
    def cost_buy(self) -> float:
        pass

    @property
    def cost_sell(self) -> float:
        pass

    @property
    def fees_buy(self) -> float:
        pass

    @property
    def fees_sell(self) -> float:
        pass

    # --------------------------------
    # --------------------------------


# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
