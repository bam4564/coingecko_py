""" Maps url to tuple of (endpoint_name, args, kwargs) """
url_to_endpoint = {
    "https://api.coingecko.com/api/v3/ping": ("ping", (), {}),
    "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd": (
        "get_price",
        ("bitcoin", "usd"),
        {},
    ),
    "https://api.coingecko.com/api/v3/simple/token_price/ethereum?include_market_cap=true&include_24hr_vol=true&include_last_updated_at=true&contract_addresses=0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE&vs_currencies=bnb": (
        "get_token_price",
        ("ethereum", "0xB8c77482e45F1F44dE1745F52C74426C631bDD52", "bnb"),
        dict(
            include_market_cap="true",
            include_24hr_vol="true",
            include_last_updated_at="true",
        ),
    ),
    "https://api.coingecko.com/api/v3/simple/supported_vs_currencies": (
        "get_supported_vs_currencies",
        (),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins": ("get_coins", (), {}),
    "https://api.coingecko.com/api/v3/coins/list": ("get_coins_list", (), {}),
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd": (
        "get_token_price",
        ("usd"),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/bitcoin/": (
        "get_coin_by_id",
        ("bitcoin"),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/bitcoin/tickers": (
        "get_coin_ticker_by_id",
        ("bitcoin"),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=27-08-2018": (
        "get_coin_history_by_id",
        ("bitcoin", "27-08-2018"),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1": (
        "get_coin_market_chart_by_id",
        (
            "bitcoin",
            "usd",
            1,
        ),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/litecoin/status_updates": (
        "get_coin_status_updates_by_id",
        ("litecoin"),
        {},
    ),
    "https://api.coingecko.com/api/v3/coins/ethereum/contract/0x0D8775F648430679A709E98d2b0Cb6250d2887EF": (
        "get_coin_info_from_contract_address_by_id",
        (),
        dict(
            id="ethereum",
            contract_address="0x0D8775F648430679A709E98d2b0Cb6250d2887EF",
        ),
    ),
    "https://api.coingecko.com/api/v3/exchanges": ("get_exchanges_list", (), {}),
    "https://api.coingecko.com/api/v3/exchanges/list": (
        "get_exchanges_id_name_list",
        (),
        {},
    ),
    "https://api.coingecko.com/api/v3/exchanges/bitforex": (
        "get_exchanges_by_id",
        ("bitforex"),
        {},
    ),
    "https://api.coingecko.com/api/v3/exchange_rates": ("get_exchange_rates", (), {}),
    "https://api.coingecko.com/api/v3/search/trending": ("get_search_trending", (), {}),
    "https://api.coingecko.com/api/v3/global": ("get_global", (), {}),
    "https://api.coingecko.com/api/v3/finance_platforms": (
        "get_finance_platforms",
        (),
        {},
    ),
    "https://api.coingecko.com/api/v3/finance_products": (
        "get_finance_products",
        (),
        {},
    ),
}
