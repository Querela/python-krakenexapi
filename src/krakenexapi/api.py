import hashlib
import hmac
from base64 import b64decode
from base64 import b64encode
from datetime import datetime
from os import PathLike
from pathlib import Path
from time import time
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from urllib.parse import urlencode

import requests

from . import __version__

# ----------------------------------------------------------------------------

NONCE_OFFSET = -datetime(2020, 1, 1).timestamp()

API_METHODS_PUBLIC = [
    "Time",
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
            raise Exception("No key file found!")

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
    ):
        url = f"{self.api_domain}{path}"
        resp = self.session.post(url, data=data, headers=headers, timeout=timeout)

        result = resp.json()
        if result.get("error", None):
            raise Exception(result["error"])
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

    def query_public(self, method: str, data: Optional[Dict[str, Any]] = None):
        assert method in API_METHODS_PUBLIC, f"Unknown public API method: {method}"

        api_path = f"/0/public/{method}"
        if not data:
            data = dict()

        result = self._query_raw(api_path, data=data, headers={})
        return result

    def query_private(self, method: str, data: Optional[Dict[str, Any]] = None):
        assert method in API_METHODS_PRIVATE, f"Unknown private API method: {method}"

        api_path = f"/0/private/{method}"
        if not data:
            data = dict()

        data["nonce"] = self.nonce()
        headers = {"API-Key": self.__api_key, "API-Sign": self._sign(api_path, data)}

        result = self._query_raw(api_path, data=data, headers=headers)
        return result


# ----------------------------------------------------------------------------


class BasicKrakenExAPI(RawKrakenExAPI):
    def __init__(self, key: Optional[str] = None, secret: Optional[str] = None):
        super().__init__(key=key, secret=secret)


# ----------------------------------------------------------------------------
