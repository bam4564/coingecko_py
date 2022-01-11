import json

from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra
from pycoingecko_extra.utils import update_querystring
from tests.data.constants import url_to_endpoint

def get_data():
    cg = CoinGeckoAPIExtra(_log_level=20)
    # create data file for non-paginated endpoints 
    results = dict()
    for url in url_to_endpoint.keys():
        results[url] = cg._CoinGeckoAPI__request(url)
        assert results[url]
    with open("./tests/data/test_data.json", "w") as f:
        f.write(json.dumps(results, indent=4))
    # create data file for paginated endpoints. test data will contain pages 2, 3, 4
    results_paginated = dict() 
    for url, (endpoint_name, _, _) in url_to_endpoint.items(): 
        if endpoint_name in cg.paginated_fns: 
            assert "page=" not in url 
            for i in range(2, 5): 
                purl = update_querystring(url, dict(page=i, per_page=5))
                results_paginated[purl] = cg._CoinGeckoAPI__request(purl)
                assert results_paginated[purl]
    with open("./tests/data/test_data_paged.json", "w") as f:
        f.write(json.dumps(results_paginated, indent=4))
            
