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
    """Immutable singleton currency info dataclass.

    Raises
    ------
    AssertionError
        If trying to create a new `Currency` *singleton* instance
        with an already registered `symbol` identifier.
    """

    #: Currency symbol used by Kraken Exchange.
    symbol: str
    #: Alternative currency symbol. (can be same as `symbol`, often without *X*/*Z* prefix)
    name: str
    #: Number of decimals used in computation (precision).
    decimals: int
    #: Number of decimals displayed to user.
    display_decimals: int
    #: Optional. Currency symbol/glyph.
    letter: Optional[str] = None
    #: Optional. Short currency description/name.
    description: Optional[str] = None

    #: Internal. Lookup of currency to instance.
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
        """Returns :obj:`True` if currency is fiat, :obj:`False` if crypto.

        Returns
        -------
        bool
            :obj:`True` if fiat currency.
        """
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
        """Is a currency, staked on Kraken Exchange.

        Returns
        -------
        bool
        """
        return self.is_staked_onchain or self.is_staked_offchain

    # --------------------------------

    def format_value(self, value: float) -> str:
        """Formats a given `value` according to the `display_decimals`
        of the currency.

        If a currency symbol/letter exists, append it.

        Parameters
        ----------
        value : float
            The value to be formatted.

        Returns
        -------
        str
            Formatted string.
        """
        return f"{value:.{self.display_decimals}f}{self.letter or ''}"

    def round_value(self, value: float) -> float:
        """Round a given `value` to the maximum number of digits as
        specified in `decimals` of the currency.

        Parameters
        ----------
        value : float
            Number to be rounded.

        Returns
        -------
        float
            Number rounded to `decimals` digits.
        """
        return round(value, self.decimals)

    # --------------------------------

    @classmethod
    def find(cls, symbol: str) -> "Currency":
        """Finds the singleton instance of the currency described by
        the `symbol` (Kraken Exchange identifier) string.

        Returns
        -------
        krakenexapi.wallet.Currency
            Currency singleton instance.

        Raises
        ------
        KeyError
            If no `Currency` exists for the `symbol`.
        """
        return cls.__currencies[symbol.upper()]

    @classmethod
    def all_symbols(cls, unique: bool = True) -> Set[str]:
        """Return a list of all instanciated `Currency` symbols.

        This allows the retrieval of all `Currency` instances via
        :meth:`find` (with/without) duplicates.

        Parameters
        ----------
        unique : bool, optional
            Whethere the list of symbols allows for duplicate
            when used for retrieval, or not,
            by default True (no duplicates)

        Returns
        -------
        Set[str]
            Currency symbol names (used on Kraken Exchange)
        """
        if not unique:
            return set(cls.__currencies.keys())
        return {c.symbol.upper() for c in cls.__currencies.values()}

    # --------------------------------

    @classmethod
    def build_from_api(cls, api: BasicKrakenExAPIPublicMethods):
        """Uses the `api` to query a list of all currencies on
        Kraken Exchange and builds singleton instances for each
        of it.

        Parameters
        ----------
        api : BasicKrakenExAPIPublicMethods
            An API that allows to query public Kraken Exchange endpoints.
        """
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
    """Immutable singleton currency trading pair info dataclass.

    Raises
    ------
    AssertionError
        If trying to create a new `CurrencyPair` *singleton* instance
        with an already registered `symbol` identifier.
    """

    #: Trading pair symbol (used on Kraken Exchange)
    symbol: str
    #: Alternative name for trading pair.
    altname: str
    #: Visual name (human readable).
    name: str
    pair_decimals: int
    #: Base currency
    base: Currency
    #: Quote currency, determines value/price for `base` currency.
    quote: Currency
    #: Minimum amount of `base` currency for a new order.
    ordermin: Optional[float] = None

    #: Internal. Registered `CurrencyPair` singletons.
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
        """Trading pair between crypto and fiat currency.

        Returns
        -------
        bool
        """
        return not self.base.is_fiat and self.quote.is_fiat

    @property
    def is_crypto2crypto(self) -> bool:
        """Trading pair between two crypto currencies.

        Returns
        -------
        bool
        """
        return not self.base.is_fiat and not self.quote.is_fiat

    @property
    def is_fiat2fiat(self) -> bool:
        """Trading pair between two fiat currencies.

        Returns
        -------
        bool
        """
        return self.base.is_fiat and self.quote.is_fiat

    # --------------------------------

    @classmethod
    def find(cls, symbol: str) -> "CurrencyPair":
        """Find the singleton `CurrencyPair` instance for the given
        `symbol` names. (as used on Kraken Exchange)

        Returns
        -------
        krakenexapi.wallet.CurrencyPair
            The `CurrencyPair` singleton instance.

        Raises
        ------
        KeyError
            If no `CurrencyPair` exists for the `symbol`.
        """
        return cls.__currency_pairs[symbol.upper()]

    @classmethod
    def all_symbols(cls, unique: bool = True) -> Set[str]:
        """Return a list of `symbol` for all registered `CurrencyPair`
        instances.

        Parameters
        ----------
        unique : bool, optional
            Whether the list should contain all registered `symbol`
            and `name`, or just enough to allow retrieval of all
            singleton instances, by default True

        Returns
        -------
        Set[str]
            List of currency pair symbols. (used on Kraken Exchange)
        """
        if not unique:
            return set(cls.__currency_pairs.keys())
        return {c.symbol.upper() for c in cls.__currency_pairs.values()}

    # --------------------------------

    @classmethod
    def build_from_api(cls, api: BasicKrakenExAPIPublicMethods):
        """Build a list of `CurrencyPair` and optionally `Currency`
        singleton instances.

        Uses the public Kraken Exchange API to retrieve a list of
        all available currency trading pairs and build instances for
        each of it.

        Parameters
        ----------
        api : BasicKrakenExAPIPublicMethods
            An API object that allows querying the public Kraken
            Exchange endpoints.
        """
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
    """A trading transaction.

    Subclasses should be used to mark *buy* / *sell* type.
    """

    #: Currency pair, of base and quote currency.
    #: `quote` currency determines the price. `base` is the currency being traded.
    currency_pair: CurrencyPair
    # #: Type of transaction, ``buy`` or ``sell``.
    # ttype: str
    #: Price of (crypto) currency.
    price: float
    #: Amount of currency.
    amount: float
    #: Cost of `base` currency
    #: (:attr:`~krakenexapi.wallet.TradingTransaction.currency_pair`)
    #: in `quote` currency.
    cost: float
    #: Fees for transactions, in `quote` currency.
    fees: float

    # infos from orders / transactions / ledgers
    #: Timestamp of transaction.
    timestamp: datetime
    #: Transaction ID.
    txid: str
    #: Optional. Order ID associated with transaction.
    otxid: Optional[Union[float, str]] = None

    @property
    def base_currency(self) -> Currency:
        """Base currency being traded.

        Returns
        -------
        Currency
        """
        return self.currency_pair.base

    @property
    def quote_currency(self) -> Currency:
        """Quote currency. Determines the price and value of the `base_currency` currency.

        Returns
        -------
        Currency
        """
        return self.currency_pair.quote


class CryptoBuyTransaction(TradingTransaction):
    """Crypto currency buy transaction."""


class CryptoSellTransaction(TradingTransaction):
    """Crypto currency sell transaction."""


@dataclass(frozen=True)
class FundingTransaction:
    """A funding transaction.

    Subclasses show whether it is a ``deposit`` or ``withdrawal``.
    """

    #: Currency.
    currency: Currency
    # #: Transaction type, ``deposit`` or ``funding``
    # ftype: str
    #: Amount of currency in transaction.
    amount: float
    #: Timestamp of transaction.
    timestamp: datetime
    #: Fees for transaction.
    fees: float = 0.0
    #: Ledger ID.
    #: (more exact than timestamp if used in API queries)
    lxid: Optional[Union[float, int, str]] = None


class DepositTransaction(FundingTransaction):
    """Deposit transaction of (fiat) currency to Kraken Exchange."""


class WithdrawalTransaction(FundingTransaction):
    """Withdrawal transaction from the Kraken Exchange."""


# ----------------------------------------------------------------------------

# basic assumptions
# - no margin / leverage
# - dead simple - fiat<->crypto trading only
# - aka spot-trading


class Asset:
    """Wrapper around a `Currency` and `api` for easy asset win/loss
    computation.
    """

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
        """Return :obj:`True` if the :attr:`currency` has transactions.

        Returns
        -------
        bool
            :obj:`True` if transactions exist.
        """
        return bool(self.__transactions)

    # --------------------------------

    @property
    def currency(self) -> Currency:
        """The asset currency.

        Returns
        -------
        Currency
        """
        return self.__currency

    @property
    def amount(self) -> float:
        """Amount of :attr:`currency` the user has on Kraken Exchange
        since the last update.

        Returns
        -------
        float
            Amount of currency.
        """
        return self.__amount

    # --------------------------------

    # TODO: check and compute for all transactions quote currency values to
    # selected quote currency!!

    # NOTE: transfer transactions (aka staking) can be ignored?
    # --> we query amount, staking has no fees(?), nothing to do with fiat?

    @property
    def amount_buy(self) -> float:
        """Total amount of :attr:`currency` being bought.

        Retrieved from API via transactions.

        Returns
        -------
        float
            total amount of currency bought.
        """
        return sum(
            t.amount for t in self.__transactions if isinstance(t, CryptoBuyTransaction)
        )

    @property
    def amount_sell(self) -> float:
        """Total amount of :attr:`currency` being sold.

        Retrieved from API via transactions.

        Returns
        -------
        float
            total amount of currency sold.
        """
        return sum(
            t.amount
            for t in self.__transactions
            if isinstance(t, CryptoSellTransaction)
        )

    @property
    def amount_by_transactions(self) -> float:
        """Total of bought (:attr:`amount_buy`) and sold
        (:attr:`amount_sell`) amount.

        Returns
        -------
        float
            Amount of currency just by buy/sell transactions.

        Notes
        -----

        .. math::

            amount = amount_{buy} - amount_{sell}
        """
        return self.amount_buy - self.amount_sell

    @property
    def amount_staked(self) -> float:
        raise NotImplementedError()

    @property
    def amount_unstaked(self) -> float:
        raise NotImplementedError()

    @property
    def amount_stake_rewards(self) -> float:
        raise NotImplementedError()

    @property
    def amount_by_transfers(self) -> float:
        raise NotImplementedError()

    @property
    def price_buy_avg(self) -> float:
        """Average price of all *buy* transactions.

        Returns
        -------
        float
            average buy price

        Notes
        -----

        Price calculation

        .. math::

            price_{buy} = \\frac{\\sum cost_{buy}}{\\sum amount_{buy}}
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        if not txs:
            return float("nan")
        # price * amount = cost
        # price = cost / amount
        return sum([t.cost for t in txs]) / sum([t.amount for t in txs])

    @property
    def price_sell_avg(self) -> float:
        """Average price of all *sell* transactions.

        Returns
        -------
        float
            average sell price

        See also
        --------
        price_buy_avg
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        if not txs:
            return float("nan")
        return sum([t.cost for t in txs]) / sum([t.amount for t in txs])

    @property
    def price_avg(self) -> float:
        """Average price based on :attr:`cost` by transaction and current :attr:`amount`.

        Returns
        -------
        float
            average price

        See also
        --------
        cost, amount
        """
        return -self.cost / self.amount

    def price_for_noloss(self, fees_sell: float = 0.26) -> float:
        """Minimum price that should be used for *sell* if no loss
        should be incurred. Prices larger than the noloss price will
        be wins.

        Parameters
        ----------
        fees_sell : float, optional
            Kraken Exchange *sell* fees, by default 0.26 (maximum for market orders)

        Returns
        -------
        float
            noloss price (based on quote currency)

        Note
        ----
        Current computation may not be completely correct but should
        be rather close. **Please** verify manually! (e.g. adjust price ±5%)

        .. math::

            price_{no loss} = price_{avg} * \\frac{1 + fees_{total}}{1 - fees_{sell}}

        with :math:`fees_{total}` being all fees incurred through transactions

        See also
        --------
        price_avg, fees_percentage
        """
        fees_sum = self.fees_percentage
        assert 0 <= fees_sum <= 0.26
        return self.price_avg * ((1 + fees_sum / 100) / (1 - fees_sell / 100))

    @property
    def cost_buy(self) -> float:
        """Sum of costs of *buy* transactions, based on `quote` currency.

        Returns
        -------
        float
            total costs of buy transactions (without fees)
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        return sum([t.cost for t in txs])

    @property
    def cost_sell(self) -> float:
        """Sum of costs of *sell* transactions, based on `quote` currency.

        Returns
        -------
        float
            total costs of sell transactions (without fees)
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        return sum([t.cost for t in txs])

    @property
    def cost(self) -> float:
        """Total costs computed by :attr:`cost_buy` and :attr:`cost_sell`.

        So, only costs computed by transactions.
        Negative costs means that costs of *buy* is higher than *sell*,
        positive costs means the opposite. (Positive costs would mean a
        win based on transactions alone.)

        Returns
        -------
        float
            Difference of costs for *buy* and *sell*

        Notes
        -----

        .. math::

            cost = - cost_{buy} + cost_{sell}

        See also
        --------
        cost_buy, cost_sell
        fees
        """
        return -self.cost_buy + self.cost_sell

    @property
    def fees_buy(self) -> float:
        """Fees incurred by *buy* transactions.

        Returns
        -------
        float
            total sum of fees
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoBuyTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees_sell(self) -> float:
        """Fees incurred by *sell* transactions.

        Returns
        -------
        float
            total sum of fees
        """
        txs = [t for t in self.__transactions if isinstance(t, CryptoSellTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees(self) -> float:
        """Total sum of fees for both *buy* and *sell* transactions.

        Returns
        -------
        float
            total sum of fees

        See also
        --------
        fees_buy, fees_sell
        fees_percentage
        """
        return sum([t.fees for t in self.__transactions])

    @property
    def fees_percentage(self) -> float:
        """Percentage of fees compared to costs, of transactions.

        Returns
        -------
        float
            fee percentage, see Kraken Exchange fees


        Notes
        -----

        .. math::

            fees_{\\%} = 100 * \\frac{fees}{cost_{buy} + cost_{sell}}
        """
        return 100 * self.fees / (self.cost_buy + self.cost_sell)

    @property
    def is_loss(self) -> bool:
        """Loss based on transactions. Loss if costs for *buy* higher
        than *sell*.

        Returns
        -------
        bool
            :obj:`True` if loss (i.e. higher costs for *buy*)
        """
        return (self.cost - self.fees) <= 0

    @property
    def is_loss_at_market_price_sell(self) -> bool:
        # 1) check current price lower than noloss price
        # 2) check amount * market price + cost < 0
        raise NotImplementedError()

    # --------------------------------
    # --------------------------------


class Fund:
    """Wrapper around fiat `Currency` info and computations."""

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
        """Return :obj:`True` if the :attr:`currency` has ledger
        entries for *deposit* and *withdrawal*.

        Returns
        -------
        bool
            :obj:`True` if transactions exist.
        """
        return bool(self.__transactions)

    # --------------------------------

    @property
    def currency(self) -> Currency:
        """The fund fiat currency.

        Returns
        -------
        Currency
        """
        return self.__currency

    @property
    def amount(self) -> float:
        """Amount of :attr:`currency` the user has on Kraken Exchange
        since the last update.

        Returns
        -------
        float
            Amount of currency.
        """
        return self.__amount

    # --------------------------------

    @property
    def amount_deposit(self) -> float:
        """Total amount of :attr:`currency` being deposited.

        Retrieved from API via ledger entries.

        Returns
        -------
        float
            total amount of currency deposited.
        """
        return sum(
            t.amount for t in self.__transactions if isinstance(t, DepositTransaction)
        )

    @property
    def amount_withdrawal(self) -> float:
        """Total amount of :attr:`currency` being withdrawn.

        Retrieved from API via ledger entries.

        Returns
        -------
        float
            total amount of currency withdrawn.
        """
        return sum(
            t.amount
            for t in self.__transactions
            if isinstance(t, WithdrawalTransaction)
        )

    @property
    def amount_by_transactions(self) -> float:
        """Total of deposited (:attr:`amount_deposit`) and withdrawn
        (:attr:`amount_withdrawal`) amount.

        Returns
        -------
        float
            Amount of currency just by deposit/withdrawal transactions.

        Notes
        -----

        .. math::

            amount = amount_{deposit} - amount_{withdrawal}
        """
        return self.amount_deposit - self.amount_withdrawal

    @property
    def fees_deposit(self) -> float:
        """Fees incurred by *deposit* transactions (ledgers).

        Returns
        -------
        float
            total sum of fees
        """
        txs = [t for t in self.__transactions if isinstance(t, DepositTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees_withdrawal(self) -> float:
        """Fees incurred by *withdrawal* transactions (ledgers).

        Returns
        -------
        float
            total sum of fees
        """
        txs = [t for t in self.__transactions if isinstance(t, WithdrawalTransaction)]
        return sum([t.fees for t in txs])

    @property
    def fees(self) -> float:
        """Total sum of fees for both *deposit* and *withdrawal* transactions.

        Returns
        -------
        float
            total sum of fees

        See also
        --------
        fees_deposit, fees_withdrawal
        fees_percentage
        """
        return sum([t.fees for t in self.__transactions])

    @property
    def fees_percentage(self) -> float:
        """Percentage of fees compared to amount of fiat currency.

        Returns
        -------
        float
            fee percentage


        Notes
        -----

        .. math::

            fees_{\\%} = 100 * \\frac{fees}{amount_{deposit} + amount_{withdrawal}}
        """
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
        """Update assets and funds."""
        self._update_assets()
        self._update_funds()

    def _update_assets(self):
        """Update internal dictionary of :class:`Asset`.

        If no assets exist, create an initial dictionary of assets.

        Check if new transactions found, then update all assets.
        If `_last_txid` is not :obj:`None` then query a subset of
        trading transactions to reduce traffic/calls.
        """
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
        """Update internal dictionary of :class:`Fund`.

        If no assets exist, create an initial dictionary of funds.

        Check if new funding transactions found, then update all funds.
        If `_last_lxid` is not :obj:`None` then query a subset of
        funding transactions to reduce traffic/calls.
        """
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
        """Retrieve a full list of currencies used on Kraken Exchange
        by the user.

        Current balance might not even show currency because sold,
        withdrawn or staked etc.

        1. Will look for currencies by trading transactions,
        2. then will look at deposit/withdrawals ledger entries,
        3. **WIP** then staking/transfering ledger entries,
        4. Currencies listed in current account balance.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API object that allows querying private endpoints

        Returns
        -------
        List[Currency]
            List of all Currencies used by trader.

        See also
        --------
        get_account_crypto_currencies, get_account_fiat_currencies
        """
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
        """Return a list of crypto currencies used by the trader.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance with access to private Kraken Exchange endpoints.

        Returns
        -------
        List[Currency]
            List of crypto currencies
        """
        crs = Wallet.get_all_account_currencies(api)
        crs = [c for c in crs if not c.is_fiat]
        return list(crs)

    @staticmethod
    def get_account_fiat_currencies(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ) -> List[Currency]:
        """Return a list of fiat currencies used by the trader.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance with access to private Kraken Exchange endpoints.

        Returns
        -------
        List[Currency]
            List of fiat currencies
        """
        crs = Wallet.get_all_account_currencies(api)
        crs = [c for c in crs if c.is_fiat]
        return list(crs)

    @staticmethod
    def build_assets_from_api(
        api: BasicKrakenExAPIPrivateUserDataMethods,
        fiat_currency: Optional[Currency] = None,
    ) -> List[Asset]:
        """Build a list of :class:`Asset` from the list of crypto
        currencies of the trader.

        Optionally set a quote currency for computations.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance with access to private Kraken Exchange endpoints.
        fiat_currency : Optional[Currency], optional
            Fiat currency for asset value computations, by default None

        Returns
        -------
        List[Asset]
            List of crypto currency assets.
        """
        if not fiat_currency:
            fiat_currency = Currency.find("zeur")
        crs = Wallet.get_account_crypto_currencies(api)
        assets = [Asset(c, api, fiat_currency) for c in crs]
        return assets

    @staticmethod
    def build_funds_from_api(
        api: BasicKrakenExAPIPrivateUserDataMethods,
    ):
        """Build a list of :class:`Fund` from the list of fiat
        currencies of the trader.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance with access to private Kraken Exchange endpoints.

        Returns
        -------
        List[Fund]
            List of fiat currency funds.
        """
        crs = Wallet.get_account_fiat_currencies(api)
        funds = [Fund(c, api) for c in crs]
        return funds

    @staticmethod
    def build_funding_transactions(
        api: BasicKrakenExAPIPrivateUserDataMethods,
        start: Optional[Union[int, float, str]] = None,
        sort: bool = True,
    ) -> List[FundingTransaction]:
        """Build a list of funding transactions based on ledger entries.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance to query private Kraken Exchange endpoints
        start : Optional[Union[int, float, str]], optional
            Start timestamp or ledger LXID, by default None
        sort : bool, optional
            Whether to sort transactions by timestamp ascending, by default True

        Returns
        -------
        List[FundingTransaction]
            List of funding transactions

        Raises
        ------
        RuntimeError
            On unknown funding (*deposit*/*withdrawal*) transaction type.
        """
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
                raise RuntimeError(f"Unknown transaction type: {info['type']}")
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
        """Build a list of trading transactions.

        Parameters
        ----------
        api : BasicKrakenExAPIPrivateUserDataMethods
            An API instance to query private Kraken Exchange endpoints.
        start : Optional[Union[int, float, str]], optional
            Start unix timestamp or transaction TXID, by default None
        sort : bool, optional
            Whether to sort transactions by timestamp ascending, by default True

        Returns
        -------
        List[TradingTransaction]
            List of trading transactions

        Raises
        ------
        RuntimeError
            On unknown transaction type.
        """
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

    # --------------------------------

    # TODO:
    # - total value
    # - win/loss
    # - pretty printing
    # - export to Excel/pandas.DataFrame

    # --------------------------------


# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
