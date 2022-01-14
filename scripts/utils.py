import re
import json

import urllib.parse as urlparse
from urllib.parse import urlencode

FORMATTED_SPEC_PATH = "./swagger_specs/swagger_processed.json"


def get_url_base():
    with open(FORMATTED_SPEC_PATH, "r") as f:
        spec = json.loads(f.read())
    host = spec["host"]
    basePath = spec["basePath"]
    schemes = spec["schemes"]
    assert len(schemes) == 1
    scheme = schemes[0]
    url_parts = [scheme, host, basePath, "", "", ""]
    url = urlparse.urlunparse(url_parts)
    return url


def materialize_url_template(url_template, args, kwargs):
    """Converts url template to url to request from api by adding prefix and encoding args, kwargs

    input:
        url_template = "/coins/{id}/contract/{contract_address}/market_chart/range"
        args = ["ethereum", "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"]
        kwargs = {
            "vs_currency": "eur",
            "from": "1622520000",
            "to": "1638334800"
        }

    output:
        https://api.coingecko.com/api/v3/coins/ethereum/contract/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984/market_chart/range?vs_currency=eur&from=1622520000&to=1638334800
    """
    url_base = get_url_base()
    url_base_parts = list(urlparse.urlparse(url_base))
    # transform /coins/{id}/contract/{contract_address} ---> /coins/{0}/contract/{1}
    path_args = re.findall("({[^}]*})", url_template)
    url = url_template
    for i, p in enumerate(path_args):
        url = url.replace(p, "{" + str(i) + "}")
    # construct full url
    url_parts = list(urlparse.urlparse(url))
    url_parts[0] = url_base_parts[0]
    url_parts[1] = url_base_parts[1]
    # add args to path
    url_parts[2] = url_base_parts[2] + url.format(*args)
    # add kwargs as query string parameters
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(kwargs)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)
    return url
