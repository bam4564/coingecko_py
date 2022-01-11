import json
import os
import pytest
import requests
import requests.exceptions
import responses
import unittest
from requests.exceptions import HTTPError

from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra, error_msgs
from tests.data.constants import url_to_endpoint

TEST_ID = "TESTING_ID"


@pytest.fixture(scope="class")
def cg(request):
    request.cls.cg = CoinGeckoAPIExtra()


@pytest.fixture(scope="class")
def expected_response(request):
    with open("tests/data/test_data.json", "r") as f:
        request.cls.expected_response = json.loads(f.read())


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.mark.usefixtures("cg")
@pytest.mark.usefixtures("expected_response")
class TestWrapper(unittest.TestCase):
    @responses.activate
    def test_connection_error_queued(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.ping(qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            self.cg.execute_queued()

    @responses.activate
    def test_success_normal(self):
        for url, (endpoint_name, args, kwargs) in url_to_endpoint.items():
            try:
                expected_response = self.expected_response[url]
                assert expected_response
                responses.add(
                    responses.GET,
                    url,
                    json=expected_response,
                    status=200,
                )
                response = getattr(self.cg, endpoint_name)(*args, **kwargs)
                if endpoint_name == "get_global":
                    response = {"data": response}
                assert response == expected_response
            except:
                # Log call info on failure
                print(url)
                print(endpoint_name)
                print(args)
                print(kwargs)
                raise

    @responses.activate
    def test_success_queued(self):
        for url, (endpoint_name, args, kwargs) in url_to_endpoint.items():
            try:
                expected_response = self.expected_response[url]
                assert expected_response
                responses.add(
                    responses.GET,
                    url,
                    json=expected_response,
                    status=200,
                )
                getattr(self.cg, endpoint_name)(*args, **kwargs, qid=TEST_ID)
                assert len(self.cg._queued_calls) == 1
                response = self.cg.execute_queued()[TEST_ID]
                if endpoint_name == "get_global":
                    response = {"data": response}
                assert response == expected_response
            except:
                # Log call info on failure
                print(url)
                print(endpoint_name)
                print(args)
                print(kwargs)
                raise
