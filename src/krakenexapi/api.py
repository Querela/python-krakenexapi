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
from wrapt import synchronized

from . import __version__
from .exceptions import APIArgumentUsageError
from .exceptions import APIPermissionDenied
from .exceptions import APIRateLimitExceeded
from .exceptions import KrakenExAPIError
from .exceptions import NoPrivateKey
from .exceptions import NoSuchAPIMethod

# ----------------------------------------------------------------------------


__all__ = [
    "BasicKrakenExAPI",
    "KrakenExAPIError",
    "APIRateLimitExceeded",
    "APIArgumentUsageError",
    "APIPermissionDenied",
    "NoPrivateKey",
    "NoSuchAPIMethod",
]


# ----------------------------------------------------------------------------

#: Nonce value *offset*, nonce value will start from year ``2021``
NONCE_OFFSET = -datetime(2021, 1, 1).timestamp()

#: List of allowed public endpoints
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
#: List of allowed private endpoints
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
    #
    "GetWebSocketsToken",
]

API_METHODS_NO_RETRY = [
    "AddOrder",
    "AddExport",
    "Withdraw",
    "WalletTransfer",
]

# ----------------------------------------------------------------------------


class RawKrakenExAPI:
    """Raw Kraken Exchange API adspter."""

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
        else:
            path = Path(path)
            if path.is_dir():
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
        # NOTE: dev
        # print(f"query: {path}: {data}")
        url = f"{self.api_domain}{path}"
        resp = self.session.post(url, data=data, headers=headers, timeout=timeout)

        result = resp.json()
        if result.get("error", None):
            if "EAPI:Rate limit exceeded" in result["error"]:
                raise APIRateLimitExceeded()
            if "EGeneral:Invalid arguments" in result["error"]:
                raise APIArgumentUsageError()
            if "EGeneral:Permission denied" in result["error"]:
                raise APIPermissionDenied()
            if "EAPI:Invalid nonce" in result["error"]:
                pass
            raise KrakenExAPIError("Recieved response: " + ", ".join(result["error"]))
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

    def query_public(self, method: str, **kwargs) -> Dict[str, Any]:
        if method not in API_METHODS_PUBLIC:
            raise NoSuchAPIMethod(f"Unknown public API method: {method}")

        api_path = f"/0/public/{method}"
        data = kwargs if kwargs else {}

        result = self._query_raw(api_path, data=data, headers={})
        return result

    def query_private(
        self, method: str, otp: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        if method not in API_METHODS_PRIVATE:
            raise NoSuchAPIMethod(f"Unknown private API method: {method}")

        api_path = f"/0/private/{method}"
        data = kwargs if kwargs else {}

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
        if data and all(c in "0123456789.-" for c in data):
            data = float(data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = _fix_float_type(v)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = _fix_float_type(data[i])
    return data


# ------------------------------------


@synchronized
class _CallRateLimitInfo:
    def __init__(self, limit: float = 1, cost: float = 1, decay: float = 1.0):
        self._limit = limit
        self._cost = cost
        self._decay = decay

        self._counter: float = 0.0
        self._last_time: float = 0.0

    def decay(self):
        now = time()
        seconds_gone = now - self._last_time
        self._counter = max(0.0, self._counter - self._decay * seconds_gone)
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

    def set_exceeded(self):
        self._counter = self._limit + self._decay * 3
        self._last_time = time()

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
        crl = _CallRateLimitInfo(limit=float("inf"), cost=0.0, decay=0.0)

        if self._tier:
            tier = self._tier.lower().strip()
            if tier == "starter":
                crl = _CallRateLimitInfo(limit=15.0, cost=1.0, decay=0.33)

            elif tier == "intermediate":
                crl = _CallRateLimitInfo(limit=20.0, cost=1.0, decay=0.5)
            elif tier == "pro":
                crl = _CallRateLimitInfo(limit=20.0, cost=1.0, decay=1.0)

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
            cost: Optional[int] = self._get_cost(method)
        else:
            crl = self._crl_public
            cost = None

        # NOTE: dev
        # print(
        #     f"crl: {method} c:{cost} {crl._counter:.1f}/{crl._limit} - {crl.time_to_call(cost or 1)}s"
        # )

        if wait:
            crl.check_and_wait(cost)
            return True
        return crl.check(cost)

    def set_exceeded(self, method):
        if self._is_private(method):
            crl = self._crl_private
        else:
            crl = self._crl_public

        crl.set_exceeded()


class RawCallRateLimitedKrakenExAPI(RawKrakenExAPI):
    def __init__(
        self,
        key: Optional[str] = None,
        secret: Optional[str] = None,
        tier: Optional[str] = "Starter",
    ):
        super().__init__(key=key, secret=secret)
        self.__crl = KrakenExAPICallRateLimiter(tier)
        self._num_retries = 3

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
        try:
            result = super()._query_raw(path, data, headers, timeout)
        except APIRateLimitExceeded:
            sleep(1)
            self.__crl.set_exceeded(method)
            raise

        return result

    def query_public(self, method: str, **kwargs) -> Dict[str, Any]:
        try:
            return super().query_public(method, **kwargs)
        except APIRateLimitExceeded:
            # retry with exponential backoff
            if self._num_retries > 0:
                for i in range(self._num_retries):
                    # NOTE: dev
                    # print(f"Retry #{i+1}/{self._num_retries} for public: {method}")
                    sleep(2 ** i)
                    self.__crl.set_exceeded(method)

                    try:
                        return super().query_public(method, **kwargs)
                    except APIRateLimitExceeded:
                        pass

            raise

    def query_private(
        self, method: str, otp: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        try:
            return super().query_private(method, otp=otp, **kwargs)
        except APIRateLimitExceeded:
            # retry with exponential backoff
            if self._num_retries > 0 and method not in API_METHODS_NO_RETRY:
                for i in range(self._num_retries):
                    # NOTE: dev
                    # print(f"Retry #{i+1}/{self._num_retries} for private: {method}")
                    sleep(2 ** (i + 1))
                    self.__crl.set_exceeded(method)
                    # self.__crl.check_call(method, wait=True)

                    try:
                        return super().query_private(method, otp=otp, **kwargs)
                    except APIRateLimitExceeded:
                        pass

            raise

    # --------------------------------


# ------------------------------------


class BasicKrakenExAPIPublicMethods:
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
        data["pair"] = pair
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
        data["pair"] = pair
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
        self, pair: str, since: Optional[str] = None
    ) -> Tuple[List[List[Any]], int]:
        data = {}
        data["pair"] = pair
        if since:
            data["since"] = since

        result = self.query_public("Trades", **data)
        last = result.pop("last", None)
        result = result[list(result.keys())[0]]

        return result, last

    def get_recent_trades(
        self, pair: str, since: Optional[str] = None
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
        data["pair"] = pair
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


class BasicKrakenExAPIPrivateUserDataMethods:
    def get_account_balance(self) -> Dict[str, float]:
        result = self.query_private("Balance")

        result = _fix_float_type(result)

        return result

    def get_trade_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        data = {}
        if asset:
            data["asset"] = asset

        result = self.query_private("TradeBalance", **data)

        result = _fix_float_type(result)

        return result

    # --------------------------------

    def get_open_orders(
        self, trades: Optional[bool] = None, userref: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if trades is not None:
            data["trades"] = 1 if trades else 0
        if userref:
            data["userref"] = userref

        result = self.query_private("OpenOrders", **data)

        result = result["open"]
        result = _fix_float_type(result)

        return result

    def get_closed_orders(
        self,
        trades: Optional[bool] = None,
        userref: Optional[str] = None,
        start: Optional[Union[int, float, str]] = None,
        end: Optional[Union[int, float, str]] = None,
        offset: Optional[int] = None,
        closetime: Optional[str] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], int]:
        data = {}
        if trades is not None:
            data["trades"] = 1 if trades else 0
        if userref:
            data["userref"] = userref
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        if offset:
            # NOTE: not sure whether it works
            data["ofs"] = offset
        if closetime:
            assert closetime in ("open", "close", "both")
            data["closetime"] = closetime

        result = self.query_private("ClosedOrders", **data)

        amount = result["count"]
        result = result["closed"]
        result = _fix_float_type(result)

        return result, amount

    def get_orders_info(
        self,
        txid: Union[str, List[str]],
        trades: Optional[bool] = None,
        userref: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if isinstance(txid, str):
            txid = [txid]
        assert len(txid) <= 50
        data["txid"] = ",".join(txid)
        if trades is not None:
            data["trades"] = 1 if trades else 0
        if userref:
            data["userref"] = userref

        result = self.query_private("QueryOrders", **data)

        result = _fix_float_type(result)

        return result

    def get_trades_history(
        self,
        type: Optional[str] = None,
        trades: Optional[bool] = None,
        start: Optional[Union[int, float, str]] = None,
        end: Optional[Union[int, float, str]] = None,
        offset: Optional[int] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], int]:
        data = {}
        if trades is not None:
            data["trades"] = 1 if trades else 0
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        if offset:
            # NOTE: not sure whether it works
            data["ofs"] = offset
        if type:
            assert type in (
                "all",
                "any position",
                "closed position",
                "closing position",
                "no position",
            )
            data["type"] = type

        result = self.query_private("TradesHistory", **data)

        amount = result["count"]
        result = result["trades"]
        result = _fix_float_type(result)

        return result, amount

    def get_trades_info(
        self,
        txid: Union[str, List[str]],
        trades: Optional[bool] = None,
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if isinstance(txid, str):
            txid = [txid]
        assert len(txid) <= 20
        data["txid"] = ",".join(txid)
        if trades is not None:
            data["trades"] = 1 if trades else 0

        result = self.query_private("QueryTrades", **data)

        result = _fix_float_type(result)

        return result

    def get_open_positions(
        self,
        txid: Union[str, List[str]],
        docalcs: Optional[bool] = None,
        trades: Optional[bool] = None,
        consolidation: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        data = {}
        if isinstance(txid, str):
            txid = [txid]
        data["txid"] = ",".join(txid)
        if docalcs is not None:
            # data["docalcs"] = 1 if docalcs else 0
            data["docalcs"] = docalcs
        if consolidation is not None:
            data["consolidation"] = consolidation

        result = self.query_private("OpenPositions", **data)

        result = _fix_float_type(result)

        return result

    def get_ledgers(
        self,
        asset: Optional[Union[str, List[str]]] = None,
        type: Optional[str] = None,
        start: Optional[Union[int, float, str]] = None,
        end: Optional[Union[int, float, str]] = None,
        offset: Optional[int] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], int]:
        data = {}
        if asset:
            if isinstance(asset, str):
                asset = [asset]
            data["asset"] = ",".join(asset)
        if type:
            assert type in ("all", "deposit", "withdrawal", "trade", "margin")
            data["type"] = type
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        if offset:
            # NOTE: not sure whether it works
            data["ofs"] = offset

        result = self.query_private("Ledgers", **data)

        amount = result["count"]
        result = result["ledger"]
        result = _fix_float_type(result)

        return result, amount

    def get_ledgers_info(self, lid: Union[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        data = {}
        if isinstance(lid, str):
            lid = [lid]
        assert len(lid) <= 20
        data["id"] = ",".join(lid)

        result = self.query_private("QueryLedgers", **data)

        result = _fix_float_type(result)

        return result

    # --------------------------------

    def get_trade_volume(
        self,
        pair: Optional[Union[str, List[str]]] = None,
        fee_info: Optional[bool] = None,
    ) -> Dict[str, Any]:
        data = {}
        if pair:
            if isinstance(pair, str):
                pair = [pair]
            data["pair"] = ",".join(pair)
        if fee_info is not None:
            data["fee-info"] = 1 if fee_info else 0

        result = self.query_private("TradeVolume", **data)

        result = _fix_float_type(result)

        return result

    # --------------------------------

    # exports

    # --------------------------------


class BasicKrakenExAPIPrivateUserTradingMethods:
    pass

    # --------------------------------


class BasicKrakenExAPIPrivateUserFundingMethods:
    pass

    # --------------------------------


class BasicKrakenExAPIPrivateWebsocketMethods:
    def get_websocket_token(self) -> str:
        result = self.query_private("GetWebSocketsToken")
        # assert result["expires"] == 900
        result = result["token"]
        return result

    # --------------------------------


class BasicKrakenExAPI(
    BasicKrakenExAPIPublicMethods,
    BasicKrakenExAPIPrivateUserDataMethods,
    BasicKrakenExAPIPrivateUserTradingMethods,
    BasicKrakenExAPIPrivateUserFundingMethods,
    BasicKrakenExAPIPrivateWebsocketMethods,
    RawCallRateLimitedKrakenExAPI,
):
    pass

    # --------------------------------


# ----------------------------------------------------------------------------


def gather_closed_orders(
    api: BasicKrakenExAPIPrivateUserDataMethods, *args, **kwargs
) -> Dict[str, Any]:
    order_entries = dict()

    offset: int = kwargs.pop("offset", 0)
    total = offset + 1
    while offset < total:
        entries, total = api.get_closed_orders(*args, offset=offset, **kwargs)
        if not entries:
            break
        order_entries.update(entries)
        offset += len(entries)

    return order_entries


def gather_trades(
    api: BasicKrakenExAPIPrivateUserDataMethods, *args, **kwargs
) -> Dict[str, Any]:
    trade_entries = dict()

    offset = kwargs.pop("offset", 0)
    total = offset + 1
    while offset < total:
        entries, total = api.get_trades_history(*args, offset=offset, **kwargs)
        if not entries:
            break
        trade_entries.update(entries)
        offset += len(entries)

    return trade_entries


def gather_ledgers(
    api: BasicKrakenExAPIPrivateUserDataMethods, *args, **kwargs
) -> Dict[str, Any]:
    ledger_entries = dict()

    offset = kwargs.pop("offset", 0)
    total = offset + 1
    while offset < total:
        entries, total = api.get_ledgers(*args, offset=offset, **kwargs)
        # NOTE: reports incorrect total (not subset count if type filtering)
        if not entries:
            break
        ledger_entries.update(entries)
        offset += len(entries)

    return ledger_entries


# ----------------------------------------------------------------------------
