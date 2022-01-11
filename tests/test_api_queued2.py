import json
import pytest
import requests
import requests.exceptions
import responses
import unittest
from requests.exceptions import HTTPError

from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra, error_msgs

TEST_ID = "TESTING_ID"


@pytest.fixture(scope="class")
def cg(request):
    request.cls.cg = CoinGeckoAPIExtra()


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.mark.usefixtures("cg")
class TestWrapper(unittest.TestCase):
    @responses.activate
    def test_connection_error_queued(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.ping(qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            self.cg.execute_queued()

    # ---------- NEW FUNCTIONALITY ----------#

    @responses.activate
    def test_multiple_queued(self):
        bitcoin_json_sample = {
            "name": "Bitcoin",
            "tickers": [
                {
                    "base": "BTC",
                    "target": "USDT",
                    "market": {
                        "name": "BW.com",
                        "identifier": "bw",
                        "has_trading_incentive": False,
                    },
                    "last": 7963.0,
                    "    volume": 93428.7568,
                    "converted_last": {
                        "btc": 0.99993976,
                        "eth": 31.711347,
                        "usd": 7979.23,
                    },
                    "converted_volume": {
                        "btc": 93423,
                        "eth": 2962752,
                        "usd": 745489919,
                    },
                    "    bid_ask_spread_percentage": 0.111969,
                    "timestamp": "2019-05-24T11:20:14+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.bw.com/trade/btc_us    dt",
                    "coin_id": "bitcoin",
                }
            ],
        }
        history_json_sample = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "localization": {
                "en": "Bitcoin",
                "es": "Bitcoin",
                "de": "Bitcoin",
                "nl": "Bitcoin",
                "pt": "Bitcoin",
                "fr": "Bitcoin",
                "it": "Bitcoin",
                "hu": "Bitcoin",
                "ro": "Bitcoin",
                "sv": "Bitcoin",
                "pl": "Bitcoin",
                "id": "Bitcoin",
                "zh": "比特币",
                "zh-tw": "比特幣",
                "ja": "ビットコイン",
                "ko": "비트코인",
                "ru": "биткоина",
                "ar": "بيتكوين",
                "th": "บิตคอยน์",
                "vi": "Bitcoin",
                "tr": "Bitcoin",
            },
        }

        responses.add(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/tickers",
            json=bitcoin_json_sample,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=27-08-2018",
            json=history_json_sample,
            status=200,
        )

        self.cg.get_coin_ticker_by_id("bitcoin", qid="one")
        assert len(self.cg._queued_calls) == 1
        self.cg.get_coin_history_by_id("bitcoin", "27-08-2018", qid="two")
        assert len(self.cg._queued_calls) == 2
        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0

        assert response["one"] == bitcoin_json_sample
        assert response["two"] == history_json_sample

    @responses.activate
    @unittest.mock.patch("pycoingecko_extra.pycoingecko_extra.time.sleep")
    def test_multiple_rate_limited_success(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True

        # Total number of calls to make. num_calls - 1 fail due to rate limiting. Last one succeeds
        num_calls = 7

        prices_json_response = {
            "prices": [
                [1535373899623, 6756.942910425894],
                [1535374183927, 6696.894541693875],
                [1535374496401, 6689.990513793263],
                [1535374779118, 6668.291007556478],
                [1535375102688, 6703.7499879964],
                [1535375384209, 6706.898948451269],
            ]
        }
        history_json_response = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "localization": {
                "en": "Bitcoin",
                "es": "Bitcoin",
                "de": "Bitcoin",
                "nl": "Bitcoin",
                "pt": "Bitcoin",
                "fr": "Bitcoin",
                "it": "Bitcoin",
                "hu": "Bitcoin",
                "ro": "Bitcoin",
                "sv": "Bitcoin",
                "pl": "Bitcoin",
                "id": "Bitcoin",
                "zh": "比特币",
                "zh-tw": "比特幣",
                "ja": "ビットコイン",
                "ko": "비트코인",
                "ru": "биткоина",
                "ar": "بيتكوين",
                "th": "บิตคอยน์",
                "vi": "Bitcoin",
                "tr": "Bitcoin",
            },
        }

        def callback_stateful(data):
            class MockEndpoint:
                def __init__(self):
                    self.calls = 0

                def request_callback(self, request):
                    self.calls += 1
                    if self.calls == num_calls:
                        return (200, {}, json.dumps(data))
                    else:
                        raise requests.exceptions.RequestException(
                            response=MockResponse(status_code=429)
                        )

            return getattr(MockEndpoint(), "request_callback")

        # Will simulate rate limiting on first call, then second call will succeed
        self.cg._exp_limit = num_calls
        responses.add_callback(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1",
            callback=callback_stateful(prices_json_response),
            content_type="application/json",
        )
        responses.add_callback(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=27-08-2018",
            callback=callback_stateful(history_json_response),
            content_type="application/json",
        )
        self.cg.get_coin_market_chart_by_id("bitcoin", "usd", 1, qid="prices")
        self.cg.get_coin_history_by_id("bitcoin", "27-08-2018", qid="history")
        result = self.cg.execute_queued()
        assert len(responses.calls) == num_calls * 2
        # verify calls for prices
        for i in range(0, num_calls - 1):
            assert isinstance(
                responses.calls[i].response, requests.exceptions.RequestException
            )
            assert responses.calls[i].response.response.status_code == 429
        assert isinstance(
            responses.calls[num_calls - 1].response, requests.models.Response
        )
        assert responses.calls[num_calls - 1].response.status_code == 200
        assert result["prices"] == prices_json_response
        # verify calls for history
        for i in range(num_calls + 1, 2 * num_calls - 1):
            assert isinstance(
                responses.calls[i].response, requests.exceptions.RequestException
            )
            assert responses.calls[i].response.response.status_code == 429
        assert isinstance(
            responses.calls[num_calls - 1].response, requests.models.Response
        )
        assert responses.calls[num_calls - 1].response.status_code == 200
        assert result["history"] == history_json_response

    @responses.activate
    @unittest.mock.patch("pycoingecko_extra.pycoingecko_extra.time.sleep")
    def test_multiple_rate_limited_failed(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True

        # Total number of calls to make. num_calls - 1 fail due to rate limiting. Last one succeeds
        num_calls = 7

        def request_callback(request):
            raise requests.exceptions.RequestException(
                response=MockResponse(status_code=429)
            )

        # Will simulate rate limiting on first call, then second call will succeed
        self.cg._exp_limit = num_calls
        responses.add_callback(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1",
            callback=request_callback,
            content_type="application/json",
        )
        with pytest.raises(Exception) as e:
            self.cg.get_coin_market_chart_by_id("bitcoin", "usd", 1, qid="prices")
            self.cg.execute_queued()
        assert str(e.value) == error_msgs["exp_limit_reached"]
        assert len(self.cg._queued_calls) == 0

    @responses.activate
    def test_page_range_query(self):
        bitcoin_json_sample = {
            "name": "Bitcoin",
            "tickers": [
                {
                    "base": "BTC",
                    "target": "USDT",
                    "market": {
                        "name": "BW.com",
                        "identifier": "bw",
                        "has_trading_incentive": False,
                    },
                    "last": 7963.0,
                    "    volume": 93428.7568,
                    "converted_last": {
                        "btc": 0.99993976,
                        "eth": 31.711347,
                        "usd": 7979.23,
                    },
                    "converted_volume": {
                        "btc": 93423,
                        "eth": 2962752,
                        "usd": 745489919,
                    },
                    "    bid_ask_spread_percentage": 0.111969,
                    "timestamp": "2019-05-24T11:20:14+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.bw.com/trade/btc_us    dt",
                    "coin_id": "bitcoin",
                }
            ],
        }
        history_json_sample = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "localization": {
                "en": "Bitcoin",
                "es": "Bitcoin",
                "de": "Bitcoin",
                "nl": "Bitcoin",
                "pt": "Bitcoin",
                "fr": "Bitcoin",
                "it": "Bitcoin",
                "hu": "Bitcoin",
                "ro": "Bitcoin",
                "sv": "Bitcoin",
                "pl": "Bitcoin",
                "id": "Bitcoin",
                "zh": "比特币",
                "zh-tw": "比特幣",
                "ja": "ビットコイン",
                "ko": "비트코인",
                "ru": "биткоина",
                "ar": "بيتكوين",
                "th": "บิตคอยน์",
                "vi": "Bitcoin",
                "tr": "Bitcoin",
            },
        }

        responses.add(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/tickers",
            json=bitcoin_json_sample,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=27-08-2018",
            json=history_json_sample,
            status=200,
        )

        self.cg.get_coin_ticker_by_id("bitcoin", qid="one")
        assert len(self.cg._queued_calls) == 1
        self.cg.get_coin_history_by_id("bitcoin", "27-08-2018", qid="two")
        assert len(self.cg._queued_calls) == 2
        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0

        assert response["one"] == bitcoin_json_sample
        assert response["two"] == history_json_sample

    # TODO: Add tests to ensure that input kwargs that configure extension are found as instance properties
