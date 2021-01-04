# ----------------------------------------------------------------------------


class KrakenExAPIError(Exception):
    """Generic error."""


class APIRateLimitExceeded(KrakenExAPIError):
    """API Error: ``EAPI:Rate limit exceeded``."""


class APIArgumentUsageError(KrakenExAPIError, ValueError):
    """Error from Kraken API if arguments incorrectly supplied or
    used or values not supported.

    API Error: ``EGeneral:Invalid arguments``
    """


class NoPrivateKey(KrakenExAPIError):
    """Thrown if trying to use a private Kraken Exchange API without
    a private key."""


class NoSuchAPIMethod(KrakenExAPIError):
    """Error thrown if trying to use an invalid API method."""


class APIPermissionDenied(KrakenExAPIError):
    """Error when trying to call API methods without given permission.

    API Error: ``EGeneral:Permission denied``
    """


class APIInvalidNonce(KrakenExAPIError):
    """Error when trying to call API methods concurrently or out of
    order. Nonce will no be monotonic, so API throws error.

    API Error: ``EAPI:Invalid nonce``
    """


# ----------------------------------------------------------------------------
