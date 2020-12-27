krakenexapi.api
===============


.. automodule:: krakenexapi.api

Raw API
-------

.. autoclass:: krakenexapi.api.RawKrakenExAPI
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:

.. autodata:: NONCE_OFFSET

.. autodata:: API_METHODS_PUBLIC

.. autodata:: API_METHODS_PRIVATE

Notes
~~~~~
    The :meth:`~krakenexapi.api.RawKrakenExAPI.nonce` will use an offset of
    :data:`NONCE_OFFSET` for its value - so, the nonce value is comparatively
    smaller compared to the standard unix timestamp. Try to avoid using the
    same API key for different applications!

Basic Kraken Exchange API methods
---------------------------------

Wraps the endpoints in :data:`API_METHODS_PUBLIC` and :data:`API_METHODS_PRIVATE`
with simplified parameters and corrected return values.
It will try to call rate limit both public and, when provided a ``tier``
(verification level), private API endpoints to avoid possible blacklisting.
The full description of methods, parameters and return values csn be found in the `Official Kraken REST API`_.

.. _Official Kraken REST API:
    https://www.kraken.com/features/api

.. autoclass:: krakenexapi.api.BasicKrakenExAPI
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:

Public Endpoints
~~~~~~~~~~~~~~~~

.. autoclass:: krakenexapi.api.BasicKrakenExAPIPublicMethods
    :members:
    :undoc-members:
    :private-members:

Private Endpoints
~~~~~~~~~~~~~~~~~

.. autoclass:: krakenexapi.api.BasicKrakenExAPIPrivateUserDataMethods
    :members:
    :undoc-members:
    :private-members:

.. autoclass:: krakenexapi.api.BasicKrakenExAPIPrivateUserTradingMethods
    :members:
    :undoc-members:
    :private-members:

.. autoclass:: krakenexapi.api.BasicKrakenExAPIPrivateUserFundingMethods
    :members:
    :undoc-members:
    :private-members:

Call Rate Limiting
------------------

The Kraken Exchange used different quotas for its API methods, see the article `What are the API rate limits?`_.

.. _What are the API rate limits?:
   https://support.kraken.com/hc/en-us/articles/206548367-What-are-the-API-rate-limits-

.. autoclass:: krakenexapi.api._CallRateLimitInfo
    :members:
    :undoc-members:
    :private-members:

.. autoclass:: krakenexapi.api.KrakenExAPICallRateLimiter
    :members:
    :undoc-members:
    :private-members:

Exceptions
----------

.. autoexception:: krakenexapi.api.KrakenExAPIError
    :members:
    :show-inheritance:

.. autoexception:: krakenexapi.api.NoPrivateKey
    :members:
    :show-inheritance:

.. autoexception:: krakenexapi.api.NoSuchAPIMethod
    :members:
    :show-inheritance:
