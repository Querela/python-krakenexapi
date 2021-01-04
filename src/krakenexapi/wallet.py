from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from .api import BasicKrakenExAPI
from .api import BasicKrakenExAPIPrivateUserDataMethods
from .api import BasicKrakenExAPIPublicMethods
from .api import gather_ledgers
from .api import gather_trades

# ----------------------------------------------------------------------------


# see:
# - https://support.kraken.com/hc/en-us/articles/202944246-All-available-currencies-and-trading-pairs-on-Kraken
# - https://support.kraken.com/hc/en-us/articles/360039879471-What-is-Asset-S-and-Asset-M-


#: Lookup of currency name to symbol and short description.
#:
#: Notes
#: -----
#: Extracted from
#: `Kraken Cryptocurrencies <https://support.kraken.com/hc/en-us/articles/360000678446-Cryptocurrencies-available-on-Kraken>`_
#: help page on 2021-01-02.
CURRENCY_SYMBOLS = {
    # fist currencies
    "AUD": {"name": "Australian Dollar", "letter": "A$"},
    "CAD": {"name": "Canadian Dollar", "letter": "C$"},
    "CHF": {"name": "Swiss Franc", "letter": "Fr."},
    "EUR": {"name": "Euro", "letter": "€"},
    "GBP": {"name": "Pound Sterling", "letter": "£"},
    "JPY": {"name": "Japanese Yen)", "letter": "¥"},
    "USD": {"name": "US Dollar", "letter": "$"},
    # crypto currencies
    "AAVE": {"name": "Aave", "letter": "Å"},
    "ALGO": {"name": "Algorand", "letter": "Ⱥ"},
    "ANT": {"name": "Aragon", "letter": "ȁ"},
    "REP": {"name": "Augur", "letter": "Ɍ"},
    "REPV2": {"name": "Augur v2", "letter": "ɍ"},
    "BAT": {"name": "Basic Attention Token", "letter": "⟁"},
    "BAL": {"name": "Balancer", "letter": "ᙖ"},
    "XBT": {"name": "Bitcoin", "letter": "₿"},
    "BCH": {"name": "Bitcoin Cash", "letter": "฿"},
    "ADA": {"name": "Cardano", "letter": "₳"},
    "LINK": {"name": "Chainlink", "letter": "⬡"},
    "COMP": {"name": "Compound", "letter": "Ꮯ"},
    "ATOM": {"name": "Cosmos", "letter": "⚛"},
    "CRV": {"name": "Curve", "letter": "ᑕ"},
    "DAI": {"name": "Dai*", "letter": "⬙"},
    "DASH": {"name": "Dash", "letter": "Đ"},
    "MANA": {"name": "Decentraland", "letter": "Ɯ"},
    "XDG": {"name": "Dogecoin", "letter": "Ð"},
    "EOS": {"name": "EOS", "letter": "Ȅ"},
    "ETH": {"name": 'Ethereum ("Ether")', "letter": "Ξ"},
    "ETH2": {"name": "Ethereum 2", "letter": "Ξ"},  # TODO: inofficial
    "ETC": {"name": "Ethereum Classic", "letter": "ξ"},
    "FIL": {"name": "Filecoin", "letter": "ƒ"},
    "GNO": {"name": "Gnosis", "letter": "Ğ"},
    "ICX": {"name": "ICON", "letter": "𝗜"},
    "KAVA": {"name": "Kava", "letter": "Ҝ"},
    "KEEP": {"name": "Keep Network", "letter": "ķ"},
    "KSM": {"name": "Kusama", "letter": "Ķ"},
    "KNC": {"name": "Kyber Network", "letter": "Ƙ"},
    "LSK": {"name": "Lisk", "letter": "Ⱡ"},
    "LTC": {"name": "Litecoin", "letter": "Ł"},
    "MLN": {"name": "Melon", "letter": "M"},
    "XMR": {"name": "Monero", "letter": "ɱ"},
    "NANO": {"name": "Nano", "letter": "𝑁"},
    "OMG": {"name": "OmiseGO", "letter": "Ŏ"},
    "OXT": {"name": "Orchid", "letter": "Ö"},
    "PAXG": {"name": "PAX Gold", "letter": "ⓟ"},
    "DOT": {"name": "Polkadot", "letter": "●"},
    "QTUM": {"name": "Qtum", "letter": "ℚ"},
    "XRP": {"name": "Ripple", "letter": "Ʀ"},
    "SC": {"name": "Siacoin", "letter": "S"},
    "XLM": {"name": "Stellar Lumens", "letter": "*"},
    "STORJ": {"name": "Storj", "letter": "Ŝ"},
    "SNX": {"name": "Synthetix", "letter": "Š"},
    "TBTC": {"name": "tBTC", "letter": "Ţ"},
    "USDT": {"name": "Tether (Omni Layer, ERC20)*", "letter": "₮"},
    "XTZ": {"name": "Tezos", "letter": "ꜩ"},
    "GRT": {"name": "The Graph", "letter": "⌗"},
    "TRX": {"name": "Tron", "letter": "Ť"},
    "UNI": {"name": "Uniswap", "letter": "Ǖ"},
    "USDC": {"name": "USD Coin*", "letter": "ⓒ"},
    "WAVES": {"name": "WAVES", "letter": "♦"},
    "YFI": {"name": "Yearn Finance", "letter": "Ƴ"},
    "ZEC": {"name": "Zcash", "letter": "ⓩ"},
}


@dataclass(frozen=True)
class Currency:
    symbol: str
    name: str
    decimals: int
    display_decimals: int
    letter: Optional[str] = None
    description: Optional[str] = None

    __currencies: ClassVar[Dict[str, "Currency"]] = dict()

    def __post_init__(self):
        symbol = self.symbol.upper()
        name = self.name.upper()

        assert symbol not in self.__class__.__currencies
        self.__class__.__currencies[symbol] = self

        if name != symbol:
            assert name not in self.__class__.__currencies
            self.__class__.__currencies[name] = self

        name = name.split(".", 1)[0]
        # assign currency symbols
        if name in CURRENCY_SYMBOLS:
            object.__setattr__(self, "letter", CURRENCY_SYMBOLS[name]["letter"])
            object.__setattr__(self, "description", CURRENCY_SYMBOLS[name]["name"])
        else:
            # FLOW, FLOWH, FEE
            # raise RuntimeError(f"New currencies to Kraken Exchange added? - {name}")
            pass

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
        return f"{value:.{self.display_decimals}f}{self.letter or ''}"

    def round_value(self, value: float) -> float:
        return round(value, self.decimals)

    # --------------------------------

    @classmethod
    def find(cls, symbol: str) -> "Currency":
        return cls.__currencies[symbol.upper()]

    @classmethod
    def all_symbols(cls, unique: bool = True) -> Set[str]:
        if not unique:
            return set(cls.__currencies.keys())
        return {c.symbol.upper() for c in cls.__currencies.values()}

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


@dataclass(frozen=True)
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
        altname = self.altname.upper()

        assert symbol not in self.__class__.__currency_pairs
        self.__class__.__currency_pairs[symbol] = self

        if altname != symbol:
            assert altname not in self.__class__.__currency_pairs
            self.__class__.__currency_pairs[altname] = self

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
    def all_symbols(cls, unique: bool = True) -> Set[str]:
        if not unique:
            return set(cls.__currency_pairs.keys())
        return {c.symbol.upper() for c in cls.__currency_pairs.values()}

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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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
        txs = Wallet.build_trading_transactions(self.__api, self.__last_txid, sort=True)

        # TODO: always fo update of balsnce?

        if not txs:
            return

        # update last txid
        self.__last_txid = txs[-1].txid

        # filter transactions
        txs = [t for t in txs if t.currency_pair.base == self.__currency]
        known_txids = {t.txid for t in self.__transactions}
        txs = [t for t in txs if t.txid not in known_txids]

        self.__transactions.extend(txs)
        if txs:
            self.__transactions[:] = sorted(
                self.__transactions, key=lambda t: t.timestamp
            )

        # update amount
        # NOTE: that amount from transactions and from account_balance will
        # differ!
        balances = self.__api.get_account_balance()
        self.__amount = balances.get(self.__currency.symbol, 0.0)

    @property
    def has_transactions(self) -> bool:
        return bool(self.__transactions)

    # --------------------------------

    @property
    def currency(self) -> Currency:
        return self.__currency

    @property
    def amount(self) -> float:
        return self.__amount

    # --------------------------------

    # TODO: check and compute for all transactions quote currency values to
    # selected quote currency!!

    # NOTE: transfer transactions (aka staking) can be ignored?
    # --> we query amount, staking has no fees(?), nothing to do with fiat?

    @property
    def amount_by_transactions(self) -> float:
        amount_buy = sum(
            t.amount for t in self.__transactions if isinstance(t, CryptoBuyTransaction)
        )
        amount_sell = sum(
            t.amount
            for t in self.__transactions
            if isinstance(t, CryptoSellTransaction)
        )
        return amount_buy - amount_sell

    @property
    def amount_by_transfers(self) -> float:
        raise NotImplementedError()

    @property
    def price_buy_avg(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        if not txs:
            return float("nan")
        # price * amount = cost
        # price = cost / amount
        return sum([t.cost for t in txs]) / sum([t.amount for t in txs])

    @property
    def price_sell_avg(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        if not txs:
            return float("nan")
        return sum([t.cost for t in txs]) / sum([t.amount for t in txs])

    @property
    def price_avg(self) -> float:
        return -self.cost / self.amount

    def price_for_noloss(self, fees_sell: float = 0.26) -> float:
        fees_sum = self.fees_percentage
        assert 0 <= fees_sum <= 0.26
        return self.price_avg * ((1 + fees_sum / 100) / (1 - fees_sell / 100))

    @property
    def cost_buy(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        return sum([t.cost for t in txs])

    @property
    def cost_sell(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        return sum([t.cost for t in txs])

    @property
    def cost(self) -> float:
        return -self.cost_buy + self.cost_sell

    @property
    def fees_buy(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees_sell(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees(self) -> float:
        return sum([t.fees for t in self.__transactions])

    @property
    def fees_percentage(self) -> float:
        return 100 * self.fees / (self.cost_buy + self.cost_sell)

    @property
    def is_loss(self) -> bool:
        return self.cost <= 0

    @property
    def is_loss_at_market_price_sell(self) -> bool:
        # 1) check current price lower than noloss price
        # 2) check amount * market price + cost < 0
        raise NotImplementedError()

    # --------------------------------
    # --------------------------------


class Fund:
    def __init__(
        self,
        currency: Currency,
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ):
        self.__currency = currency
        self.__amount: float = 0.0
        self.__transactions: List[FundingTransaction] = list()
        self.__last_lxid: Optional[Union[int, str]] = None
        self.__api = api

        self._update()

    # --------------------------------

    def _update(self):
        # query ledgers from api
        txs = Wallet.build_funding_transactions(self.__api, self.__last_lxid, sort=True)

        if not txs:
            return

        # update last txid
        self.__last_lxid = txs[-1].lxid

        # filter transactions
        txs = [t for t in txs if t.currency == self.__currency]
        known_lxids = {t.lxid for t in self.__transactions}
        txs = [t for t in txs if t.lxid not in known_lxids]

        self.__transactions.extend(txs)
        if txs:
            self.__transactions[:] = sorted(
                self.__transactions, key=lambda t: t.timestamp
            )

        # update amount
        # NOTE: that amount from transactions and from account_balance may
        # differ?
        balances = self.__api.get_account_balance()
        self.__amount = balances.get(self.__currency.symbol, 0.0)

    @property
    def has_transactions(self) -> bool:
        return bool(self.__transactions)

    # --------------------------------

    @property
    def currency(self) -> Currency:
        return self.__currency

    @property
    def amount(self) -> float:
        return self.__amount

    # --------------------------------

    @property
    def amount_deposit(self) -> float:
        return sum(
            t.amount for t in self.__transactions if isinstance(t, DepositTransaction)
        )

    @property
    def amount_withdrawal(self) -> float:
        return sum(
            t.amount
            for t in self.__transactions
            if isinstance(t, WithdrawalTransaction)
        )

    @property
    def amount_by_transactions(self) -> float:
        return self.amount_deposit - self.amount_withdrawal

    @property
    def fees_deposit(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, DepositTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees_withdrawal(self) -> float:
        txs = [t for t in self.__transactions if isinstance(t, WithdrawalTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees(self) -> float:
        return sum([t.fees for t in self.__transactions])

    @property
    def fees_percentage(self) -> float:
        return 100 * self.fees / (self.amount_deposit + self.amount_withdrawal)

    # --------------------------------


# ----------------------------------------------------------------------------


class Wallet:
    def __init__(self, api: BasicKrakenExAPI):
        self.api = api
        self._last_txid: Optional[str] = None
        self._last_lxid: Optional[str] = None
        self._assets: Dict[Currency, Asset] = dict()
        self._funds: Dict[Currency, Fund] = dict()

    # --------------------------------

    def _update(self):
        self._update_assets()
        self._update_funds()

    def _update_assets(self):
        if not self._assets:
            txs = Wallet.build_trading_transactions(
                self.api, self._last_txid, sort=True
            )
            if not txs:
                return
            self._last_txid = txs[-1].txid

            assets = Wallet.build_assets_from_api(self.api)
            self._assets.update({a.currency: a for a in assets})
        else:
            txs = Wallet.build_trading_transactions(
                self.api, self._last_txid, sort=True
            )
            if not txs:
                return
            self._last_txid = txs[-1].txid

            for asset in self._assets.values():
                asset._update()

    def _update_funds(self):
        if not self._funds:
            txs = Wallet.build_funding_transactions(
                self.api, self._last_lxid, sort=True
            )
            if not txs:
                return
            self._last_lxid = txs[-1].lxid

            funds = Wallet.build_funds_from_api(self.api)
            self._funds.update({a.currency: a for a in funds})
        else:
            txs = Wallet.build_funding_transactions(
                self.api, self._last_lxid, sort=True
            )
            if not txs:
                return
            self._last_lxid = txs[-1].lxid

            for fund in self._funds.values():
                fund._update()

    def _check_new_transactions(self) -> bool:
        raise NotImplementedError()

    # --------------------------------

    @staticmethod
    def get_all_account_currencies(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ) -> List[Currency]:
        # crypto (fiat?) trades
        txs = Wallet.build_trading_transactions(api)
        crs = {t.currency_pair.base for t in txs} | {t.currency_pair.quote for t in txs}

        # deposits/withdrawals
        txs = Wallet.build_funding_transactions(api)
        crs |= {t.currency for t in txs}

        # transfers/staking

        # balances
        crs |= {Currency.find(n) for n in api.get_account_balance().keys()}

        return list(crs)

    @staticmethod
    def get_account_crypto_currencies(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ) -> List[Currency]:
        crs = Wallet.get_all_account_currencies(api)
        crs = [c for c in crs if not c.is_fiat]
        return list(crs)

    @staticmethod
    def get_account_fiat_currencies(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ) -> List[Currency]:
        crs = Wallet.get_all_account_currencies(api)
        crs = [c for c in crs if c.is_fiat]
        return list(crs)

    @staticmethod
    def build_assets_from_api(
        api: BasicKrakenExAPIPrivateUserDataMethods,
        fiat_currency: Optional[Currency] = None,
    ):
        if not fiat_currency:
            fiat_currency = Currency.find("zeur")
        crs = Wallet.get_account_crypto_currencies(api)
        assets = [Asset(c, api, fiat_currency) for c in crs]
        return assets

    @staticmethod
    def build_funds_from_api(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ):
        crs = Wallet.get_account_fiat_currencies(api)
        funds = [Fund(c, api) for c in crs]
        return funds

    @staticmethod
    def build_funding_transactions(
        api: BasicKrakenExAPIPrivateUserDataMethods,
        start: Optional[Union[int, float, str]] = None,
        sort: bool = True,
    ) -> List[FundingTransaction]:
        # query all entries
        funding_entries = dict()
        funding_entries.update(gather_ledgers(api, type="deposit", start=start))
        funding_entries.update(gather_ledgers(api, type="withdrawal", start=start))

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

        if sort:
            transactions = sorted(transactions, key=lambda t: t.timestamp)

        return transactions

        # --------------------------------

    @staticmethod
    def build_trading_transactions(
        api: BasicKrakenExAPIPrivateUserDataMethods,
        start: Optional[Union[int, float, str]] = None,
        sort: bool = True,
    ) -> List[TradingTransaction]:
        # query all entries
        trade_entries = gather_trades(api, start=start)

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

        if sort:
            transactions = sorted(transactions, key=lambda t: t.timestamp)

        return transactions


# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
