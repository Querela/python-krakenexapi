=====
Usage
=====

To use KrakenExApi in a project::

    import krakenexapi.api as kea
    import krakenexapi.wallet as kew

    api = kea.BasicKrakenExAPI(tier="Intermediate")
    api.load_key()
    kew.CurrencyPair.build_from_api(api)

    wallet = kew.Wallet(api)
    wallet._update()
