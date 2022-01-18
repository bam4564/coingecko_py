import logging
import unittest
from unittest.mock import patch

from py_coingecko.utils.api_meta import api_meta
from py_coingecko.utils.utils import (
    without_keys,
    with_keys,
    extract_from_querystring,
    sort_querystring,
    update_querystring,
    remove_from_querystring,
    dict_get,
    logger_temp_level,
    logger_temp_level,
)


class TestUtils(unittest.TestCase):
    def test_without_keys(self):
        data = dict(one=1, two=2, three=3, four=4)
        result = without_keys(data, "two", "four")
        expected = dict(one=1, three=3)
        assert result == expected

    def test_with_keys(self):
        data = dict(one=1, two=2, three=3, four=4)
        result = with_keys(data, "one", "three")
        expected = dict(one=1, three=3)
        assert result == expected

    def test_extract_from_querystring(self):
        url = "scheme://website.com/api/endpoint?one=notice&two=me&three=senpai"
        result = extract_from_querystring(url, ["two", "three"])
        expected = dict(two="me", three="senpai")
        assert url != expected
        assert result == expected

    def test_sort_querystring(self):
        url = "scheme://website.com/api/endpoint?one=notice&two=me&three=senpai"
        result = sort_querystring(url)
        expected = "scheme://website.com/api/endpoint?one=notice&three=senpai&two=me"
        assert url != expected
        assert result == expected

    def test_update_querystring(self):
        url = "scheme://website.com/api/endpoint?one=notice&two=me&three=senpai"
        result = update_querystring(url, dict(two="moi", four="pls"))
        expected = (
            "scheme://website.com/api/endpoint?one=notice&two=moi&three=senpai&four=pls"
        )
        assert url != expected
        assert sort_querystring(result) == sort_querystring(expected)

    def test_remove_from_querystring(self):
        url = "scheme://website.com/api/endpoint?one=notice&two=me&three=senpai"
        result = remove_from_querystring(url, ["two"])
        expected = "scheme://website.com/api/endpoint?one=notice&three=senpai"
        assert url != expected
        assert result == expected

    def test_dict_get(self):
        data = dict(one=1, two=2, three=3, four=4)
        one, four, two = dict_get(data, "one", "four", "two")
        assert one == data["one"]
        assert four == data["four"]
        assert two == data["two"]

    def test_logger_temp_level(self):
        logger = logging.getLogger("testing-logger")
        level = 42
        logger.setLevel(42)
        temp_level = 19
        assert logger.level == level
        with logger_temp_level(logger, temp_level):
            assert logger.level == temp_level
        assert logger.level == level

    def test_materialize_url_template(self):
        url_base = "https://dummy.com/api/v1"
        data = {
            "url_template": "/coins/{id}/contract/{contract_address}/market_chart/range",
            "path": ["ethereum", "0xdummyaddress"],
            "query": {"vs_currency": "eur", "to": "1638334800"},
        }
        with patch(
            "py_coingecko.utils.api_meta.api_meta.get_url_base"
        ) as patch_get_url_base:
            patch_get_url_base.return_value = url_base
            result = api_meta.materialize_url_template(
                data["url_template"], data["path"], data["query"]
            )
        expected = f"{url_base}/coins/ethereum/contract/0xdummyaddress/market_chart/range?vs_currency=eur&to=1638334800"
        assert result == expected

    def test_transform_path_query_to_args_kwargs(self):
        url_template = "/simple/token_price/{id}"
        parameters = [
            {
                "name": "id",
                "in": "path",
                "required": True,
            },
            {
                "name": "contract_addresses",
                "in": "query",
                "required": True,
            },
            {
                "name": "vs_currencies",
                "in": "query",
                "required": True,
            },
            {
                "name": "include_market_cap",
                "in": "query",
                "required": False,
            },
            {
                "name": "include_24hr_vol",
                "in": "query",
                "required": False,
            },
        ]
        path_args = ["ethereum"]
        query_args = {
            "contract_addresses": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
            "vs_currencies": "btc",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
        }
        with patch(
            "py_coingecko.utils.api_meta.api_meta.get_parameters"
        ) as patch_get_parameters:
            patch_get_parameters.return_value = parameters
            args, kwargs = api_meta.transform_path_query_to_args_kwargs(
                url_template, path_args, query_args
            )
        expected_args = [
            "ethereum",
            "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
            "btc",
        ]
        expected_kwargs = {"include_24hr_vol": "true", "include_market_cap": "true"}
        assert args == expected_args
        assert kwargs == expected_kwargs
