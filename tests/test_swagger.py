from cmath import exp
from collections import defaultdict
import json
import pytest
import unittest
import responses 
from requests.exceptions import HTTPError

# from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra, error_msgs
# from pycoingecko_extra.utils import extract_from_querystring, remove_from_querystring
# from tests.data.constants import url_to_endpoint 
from swagger_client import ApiClient, api_client
from pycoingecko_extra import CoinGeckoAPIClient
from scripts.utils import materialize_url_template
from client.swagger_client.api import CoingeckoApi

TEST_ID = "TESTING_ID"


@pytest.fixture(scope="class")
def cg(request):
    request.cls.cg = CoingeckoApi(api_client=CoinGeckoAPIClient())


@pytest.fixture(scope="class")
def expected_response(request):
    with open("data/test_api_responses.json", "r") as f:
        request.cls.expected_response = json.loads(f.read())


@pytest.fixture(scope="class")
def url_to_method(request):
    with open("data/url_to_method.json", "r") as f:
        request.cls.url_to_method = json.loads(f.read())

@pytest.fixture(scope="class")
def test_api_calls(request):
    with open("data/test_api_calls.json", "r") as f:
        request.cls.test_api_calls = json.loads(f.read())


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code

@pytest.mark.usefixtures("cg")
@pytest.mark.usefixtures("expected_response")
@pytest.mark.usefixtures("url_to_method")
@pytest.mark.usefixtures("test_api_calls")
class TestWrapper(unittest.TestCase):

    # ------------ TEST API ENDPOINTS SUCCESS / FAILURE (Normal + Queued) ----------------------

    @responses.activate
    def test_success_normal(self):
        for url_template, method_name in self.url_to_method.items(): 
            try: 
                expected_response = self.expected_response[url_template]
                assert expected_response
                test_call = self.test_api_calls[url_template]
                args = test_call['args']
                kwargs = test_call['kwargs']
                url = materialize_url_template(url_template, args, kwargs)
                responses.add(
                    responses.GET,
                    url,
                    json=expected_response,
                    status=200,
                )
                response = getattr(self.cg, method_name)(*args, **kwargs)
                assert response == expected_response
            except:
                # Log call info on failure
                print(url, args, kwargs)
                raise

    # @responses.activate
    # def test_failed_normal(self):
    #     for url, (endpoint_name, args, kwargs) in url_to_endpoint.items():
    #         responses.add(
    #             responses.GET,
    #             url,
    #             status=404,
    #         )
    #         with pytest.raises(HTTPError) as HE:
    #             getattr(self.cg, endpoint_name)(*args, **kwargs)
    #             # If we get past this call, an error was not raised
    #             print(url)
    #             print(endpoint_name)
    #             print(args)
    #             print(kwargs)
