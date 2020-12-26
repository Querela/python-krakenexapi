import hashlib
import hmac
from base64 import b64decode
from base64 import b64encode
from datetime import datetime
from os import PathLike
from pathlib import Path
from time import sleep
from time import time
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union
from urllib.parse import urlencode

import requests

from . import __version__

# ----------------------------------------------------------------------------


__all__ = [
    "RawKrakenExAPI",
    "BasicKrakenExAPI",
    "KrakenExAPIError",
    "NoPrivateKey",
    "NoSuchAPIMethod",
]


# ----------------------------------------------------------------------------

NONCE_OFFSET = -datetime(2020, 1, 1).timestamp()

API_METHODS_PUBLIC = [
    "Time",
    "SystemStatus",
    "Assets",
    "AssetPairs",
    "Ticker",
    "OHLC",
    "Depth",
    "Trades",
    "Spread",
]
API_METHODS_PRIVATE = [
    "Balance",
    "TradeBalance",
    "TradeVolume",
    "DepositMethods",
    "DepositAddresses",
    "DepositStatus",
    "WithdrawInfo",
    "Withdraw",
    "WithdrawCancel",
    "WithdrawStatus",
    "WalletTransfer",
    #
    "OpenOrders",
    "QueryOrders",
    "OpenPositions",
    "ClosedOrders",
    "QueryOrders",
    "QueryTrades",
    "TradesHistory",
    "AddOrder",
    "CancelOrder",
    #
    "Ledgers",
    "QueryLedgers",
    #
    "AddExport",
    "RetrieveExport",
    "ExportStatus",
    "RemoveExport",
]


# ----------------------------------------------------------------------------


class KrakenExAPIError(Exception):
    """Generic error"""


class NoPrivateKey(KrakenExAPIError):
    """Thrown if trying to use a private Kraken Exchange API without
    a private key."""


class NoSuchAPIMethod(KrakenExAPIError):
    """Error thrown if trying to use an invalid API method."""


# ----------------------------------------------------------------------------


class RawKrakenExAPI:
    api_domain = "https://api.kraken.com"

    def __init__(self, key: Optional[str] = None, secret: Optional[str] = None):
        self.__api_key = key
        self.__api_secret = secret

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": f"krakenexapi/{__version__}"})

    def __del__(self):
        self.session.close()

    def load_key(self, path: Optional[PathLike] = None):
        if not path:
            path = Path("kraken.key")
        elif path.is_dir():
            path = path / "kraken.key"

        if not path.exists():
            raise NoPrivateKey("No key file found!")

        key = None
        secret = None

        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line.lower().startswith("key") and "=" in line:
                    key = line.split("=", 1)[-1].lstrip()
                elif line.lower().startswith("secret") and "=" in line:
                    secret = line.split("=", 1)[-1].lstrip()

        if key and secret:
            self.__api_key = key
            self.__api_secret = secret

    # --------------------------------

    def nonce(self) -> int:
        return int((time() + NONCE_OFFSET) * 1000)

    def _query_raw(
        self,
        path: str,
        data: Dict[str, Any],
        headers: Dict[str, Any],
        timeout: Optional[Tuple[int, float]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.api_domain}{path}"
        resp = self.session.post(url, data=data, headers=headers, timeout=timeout)

        result = resp.json()
        if result.get("error", None):
            raise KrakenExAPIError("Recieved response: " + ",".join(result["error"]))
        return result["result"]

    def _sign(self, api_path: str, data: Dict[str, Any]) -> str:
        postdata = urlencode(data)
        encoded = f"""{data["nonce"]}{postdata}""".encode("utf-8")
        encoded = hashlib.sha256(encoded).digest()
        message = api_path.encode("utf-8") + encoded
        signature = hmac.new(
            b64decode(self.__api_secret), message, hashlib.sha512
        ).digest()
        signature = b64encode(signature)  # .decode("utf-8")
        return signature

    def query_public(self, method: str, **kwargs):
        if method not in API_METHODS_PUBLIC:
            raise NoSuchAPIMethod(f"Unknown public API method: {method}")

        api_path = f"/0/public/{method}"
        data = kwargs if kwargs else {}

        result = self._query_raw(api_path, data=data, headers={})
        return result

    def query_private(
        self,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        otp: Optional[str] = None,
    ):
        if method not in API_METHODS_PRIVATE:
            raise NoSuchAPIMethod(f"Unknown private API method: {method}")

        api_path = f"/0/private/{method}"
        if not data:
            data = dict()

        data["nonce"] = self.nonce()
        if otp:
            data["otp"] = otp

        if not self.__api_key or not self.__api_secret:
            raise NoPrivateKey()

        headers = {"API-Key": self.__api_key, "API-Sign": self._sign(api_path, data)}

        result = self._query_raw(api_path, data=data, headers=headers)
        return result


# ----------------------------------------------------------------------------


class _OHLCEntry(NamedTuple):
    time: int
    open: float
    high: float
    low: float
    close: float
    vwap: float
    volume: float
    count: int


class _OrderBookEntry(NamedTuple):
    price: float
    volume: float
    timestamp: int


class _RecentTradeEntry(NamedTuple):
    price: float
    volume: float
    time: float
    buy_sell: str
    market_limit: str
    miscellaneous: Optional[str] = None


class _RecentSpreadEntry(NamedTuple):
    time: int
    bid: float
    ask: float


def _fix_float_type(data: Any) -> Any:
    if isinstance(data, str):
        if data and all(c in "0123456789." for c in data):
            data = float(data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = _fix_float_type(v)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = _fix_float_type(data[i])
    return data


# ------------------------------------


class _CallRateLimitInfo:
    def __init__(self, limit: float = 1, cost: float = 1, decay: float = 1.0):
        self._limit = limit
        self._cost = cost
        self._decay = decay

        self._counter: float = 0.0
        self._last_time: float = 0.0

    def decay(self):
        now = time()
        seconds_gone = round(now - self._last_time)
        self._counter = max(0, self._counter - self._decay * seconds_gone)
        self._last_time = now

    def time_to_call(self, cost: float) -> float:
        remaining = self._limit - (self._counter + cost)
        if remaining >= 0:
            return 0.0

        seconds = (-remaining) / self._decay
        return seconds

    def can_call(self, cost: Optional[Union[int, float]] = None) -> bool:
        cost = cost if cost is not None else self._cost
        return self._counter + cost <= self._limit

    def check(self, cost: Optional[Union[int, float]] = None) -> bool:
        self.decay()
        cost = cost if cost is not None else self._cost
        ok = self.can_call(cost)
        if ok:
            self._counter += cost
        return ok

    def check_and_wait(self, cost: Optional[Union[int, float]] = None):
        self.decay()
        cost = cost if cost is not None else self._cost
        seconds = self.time_to_call(cost)
        sleep(seconds)
        self._counter += cost


class KrakenExAPICallRateLimiter:
    def __init__(self, tier: Optional[str] = None):
        self._tier = tier

        self._crl_public = _CallRateLimitInfo(limit=1.0, cost=1.0, decay=1.0)
        self._crl_private = _CallRateLimitInfo(limit=float("inf"), cost=0.0, decay=0.0)

        # private endpoint configs
        self._reset_account_crl()

        # public endpoint
        #   inc: 1
        #   decay: 1/s
        #   max: 1

    def _reset_account_crl(self):
        if self._tier == "Starter":
            crl = _CallRateLimitInfo(limit=15.0, cost=1.0, decay=0.33)

        elif self._tier == "Intermediate":
            crl = _CallRateLimitInfo(limit=20.0, cost=1.0, decay=0.5)
        elif self._tier == "Pro":
            crl = _CallRateLimitInfo(limit=20.0, cost=1.0, decay=1.0)
        else:
            crl = _CallRateLimitInfo(limit=float("inf"), cost=0.0, decay=0.0)
        self._crl_private = crl

    @staticmethod
    def _is_private(method: str):
        return method in API_METHODS_PRIVATE

    @staticmethod
    def _get_cost(method: str) -> int:
        if method in ("Ledgers", "TradesHistory", "ClosedOrders"):
            return 2
        if method in ("AddOrder", "CancelOrder"):
            return 0
        return 1

    # --------------------------------

    def check_call(self, method: str, wait: bool = True) -> bool:
        if self._is_private(method):
            crl = self._crl_private
            cost = self._get_cost(method)
        else:
            crl = self._crl_public
            cost = None

        if wait:
            crl.check_and_wait(cost)
            return True
        return crl.check(cost)


# ------------------------------------


class BasicKrakenExAPI(RawKrakenExAPI):
    def __init__(
        self,
        key: Optional[str] = None,
        secret: Optional[str] = None,
        tier: Optional[str] = None,
    ):
        super().__init__(key=key, secret=secret)
        self.__crl = KrakenExAPICallRateLimiter(tier)

    # --------------------------------

    def _query_raw(
        self,
        path: str,
        data: Dict[str, Any],
        headers: Dict[str, Any],
        timeout: Optional[Tuple[int, float]] = None,
    ) -> Dict[str, Any]:
        method = path.rsplit("/", 1)[-1]
        self.__crl.check_call(method, wait=True)
        result = super()._query_raw(path, data, headers, timeout)
        return result

    # --------------------------------

    def _get_server_time(self) -> Dict[str, Any]:
        return self.query_public("Time")

    def get_server_time(self) -> datetime:
        result = self.query_public("Time")
        dt = datetime.fromtimestamp(result["unixtime"])
        return dt

    def get_system_status(self):
        result = self.query_public("SystemStatus")
        return result

    # --------------------------------

    def get_asset_info(
        self, asset: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if asset:
            if isinstance(asset, str):
                asset = [asset]
            data["asset"] = ",".join(asset)

        result = self.query_public("Assets", **data)
        return result

    def _get_asset_pairs(
        self,
        pair: Optional[Union[str, List[str]]] = None,
        info: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if info:
            assert info in ("info", "leverage", "fees", "margin")
            data["info"] = info
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)

        result = self.query_public("AssetPairs", **data)
        return result

    def _get_asset_pairs_static_values(self) -> Dict[str, Union[int, float, str]]:
        fields = (
            "aclass_base",
            "aclass_quote",
            "fee_volume_currency",
            "lot",
            "lot_decimals",
            "lot_multiplier",
            "margin_call",
            "margin_stop",
        )

        result = self._get_asset_pairs()
        info = dict()

        for fn in fields:
            vals = list({v[fn] for v in result.values()})
            if len(vals) != 1:
                raise RuntimeError(
                    "Unexpected results, API may have changed."
                    "Please contact the library creator."
                )
            info[fn] = vals[0]

        return info

    def get_asset_pairs(
        self,
        pair: Optional[Union[str, List[str]]] = None,
        info: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        fields = (
            "aclass_base",
            "aclass_quote",
            "fee_volume_currency",
            "lot",
            "lot_decimals",
            "lot_multiplier",
            "margin_call",
            "margin_stop",
        )

        result = self._get_asset_pairs(pair, info)

        for rv in result.values():
            # fix float type
            if "ordermin" in rv:
                rv["ordermin"] = float(rv["ordermin"])

            # filter static values
            for fn in fields:
                rv.pop(fn, None)

        return result

    # --------------------------------

    def _get_ticker_information(
        self, pair: Union[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if isinstance(pair, str):
            pair = [pair]
        data["pair"] = ",".join(pair)

        result = self.query_public("Ticker", **data)
        return result

    def get_ticker_information(
        self, pair: Union[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        result = self._get_ticker_information(pair)

        # fix float types
        result = _fix_float_type(result)

        return result

    def _get_ohlc_data(
        self, pair: str, interval: Optional[int] = None, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        data = {}
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)
        if interval:
            assert interval in (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
            data["interval"] = interval
        if since:
            data["since"] = since

        result = self.query_public("OHLC", **data)
        last = result.pop("last", None)
        result = result[list(result.keys())[0]]

        return result, last

    def get_ohlc_data(
        self, pair: str, interval: Optional[int] = None, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        result, last = self._get_ohlc_data(pair, interval, since)

        result = _fix_float_type(result)

        result = list(map(_OHLCEntry._make, result))

        return result, last

    def _get_order_book(
        self, pair: str, count: Optional[int] = None
    ) -> Tuple[List, List]:
        data = {}
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)
        if count:
            data["count"] = count

        result = self.query_public("Depth", **data)
        result = result[list(result.keys())[0]]
        asks = result["asks"]
        bids = result["bids"]

        return asks, bids

    def get_order_book(
        self, pair: str, count: Optional[int] = None
    ) -> Tuple[List, List]:
        asks, bids = self._get_order_book(pair, count)

        asks = _fix_float_type(asks)
        bids = _fix_float_type(bids)

        asks = list(map(_OrderBookEntry._make, asks))
        bids = list(map(_OrderBookEntry._make, bids))

        return asks, bids

    def _get_recent_trades(
        self, pair: str, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        data = {}
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)
        if since:
            data["since"] = since

        result = self.query_public("Trades", **data)
        last = result.pop("last", None)
        result = result[list(result.keys())[0]]

        return result, last

    def get_recent_trades(
        self, pair: str, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        result, last = self._get_recent_trades(pair, since)

        result = _fix_float_type(result)

        for re in result:
            if re[-1] == "":
                re[-1] = None

        result = list(map(_RecentTradeEntry._make, result))

        return result, last

    def _get_recent_spread_data(
        self, pair: str, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        data = {}
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)
        if since:
            data["since"] = since

        result = self.query_public("Spread", **data)
        last = result.pop("last", None)
        result = result[list(result.keys())[0]]

        return result, last

    def get_recent_spread_data(
        self, pair: str, since: Optional[int] = None
    ) -> Tuple[List[List[Any]], int]:
        result, last = self._get_recent_spread_data(pair, since)

        result = _fix_float_type(result)

        result = list(map(_RecentSpreadEntry._make, result))

        return result, last

    # --------------------------------


# ----------------------------------------------------------------------------
