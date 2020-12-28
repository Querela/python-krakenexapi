from dataclasses import dataclass
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Set

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

# ----------------------------------------------------------------------------
