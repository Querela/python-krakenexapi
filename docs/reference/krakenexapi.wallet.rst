krakenexapi.wallet
==================

.. automodule:: krakenexapi.wallet

Currency
--------

They are intended to work as singletons, and therefore track of registered/created instances.

.. autoclass:: krakenexapi.wallet.Currency
    :members:

.. autoclass:: krakenexapi.wallet.CurrencyPair
    :members:

Transactions
------------

.. autoclass:: krakenexapi.wallet.TradingTransaction
    :members:

.. autoclass:: krakenexapi.wallet.CryptoBuyTransaction
    :show-inheritance:
    :members:

.. autoclass:: krakenexapi.wallet.CryptoSellTransaction
    :show-inheritance:
    :members:

.. autoclass:: krakenexapi.wallet.FundingTransaction
    :members:

.. autoclass:: krakenexapi.wallet.DepositTransaction
    :show-inheritance:
    :members:

.. autoclass:: krakenexapi.wallet.WithdrawalTransaction
    :show-inheritance:
    :members:

Assets and Wallet
-----------------

.. autoclass:: krakenexapi.wallet.Asset
    :members:

.. autoclass:: krakenexapi.wallet.Fund
    :members:

.. autoclass:: krakenexapi.wallet.Wallet
    :members:
    :private-members:
