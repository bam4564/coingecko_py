import json
import re
from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra
from tests.data.constants import url_to_endpoint

# with open('./tests/test_api.py') as f:
#     src = f.read()
#     m = set(re.findall('[\"|\'](https:\/\/api\.coingecko\.com\/api\/v3\/.*)[\"|\']', src))
#     for url in m:
#         results[url] = cg._CoinGeckoAPI__request(url)


def get_data():
    cg = CoinGeckoAPIExtra(_log_level=20)
    results = dict()
    for url in url_to_endpoint.keys():
        results[url] = cg._CoinGeckoAPI__request(url)
        assert results[url]
    with open("./tests/data/test_data.json", "w") as f:
        f.write(json.dumps(results, indent=4))
