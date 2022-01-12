from collections import defaultdict
import json
import pytest
import requests
import requests.exceptions
import responses
import unittest
from requests.exceptions import HTTPError

from pycoingecko_extra.pycoingecko_extra import CoinGeckoAPIExtra, error_msgs
from pycoingecko_extra.utils import extract_from_querystring, remove_from_querystring
from tests.data.constants import url_to_endpoint

TEST_ID = "TESTING_ID"


@pytest.fixture(scope="class")
def cg(request):
    request.cls.cg = CoinGeckoAPIExtra()


@pytest.fixture(scope="class")
def expected_response(request):
    with open("tests/data/test_data.json", "r") as f:
        request.cls.expected_response = json.loads(f.read())


@pytest.fixture(scope="class")
def expected_response_paged(request):
    with open("tests/data/test_data_paged.json", "r") as f:
        request.cls.expected_response_paged = json.loads(f.read())


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.mark.usefixtures("cg")
@pytest.mark.usefixtures("expected_response")
@pytest.mark.usefixtures("expected_response_paged")
class TestWrapper(unittest.TestCase):

    # ------------ TEST CONNECTION FAILED (Normal + Queued) ----------------------

    @responses.activate
    def test_connection_error_normal(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.ping()

    @responses.activate
    def test_connection_error_queued(self):
        self.cg.ping(qid=TEST_ID)
        assert len(self.cg._queued_calls) == 1
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.execute_queued()

    # ------------ TEST API ENDPOINTS SUCCESS / FAILURE (Normal + Queued) ----------------------

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
    def test_failed_normal(self):
        for url, (endpoint_name, args, kwargs) in url_to_endpoint.items():
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            with pytest.raises(HTTPError) as HE:
                getattr(self.cg, endpoint_name)(*args, **kwargs)
                # If we get past this call, an error was not raised
                print(url)
                print(endpoint_name)
                print(args)
                print(kwargs)

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

    @responses.activate
    def test_failed_queued(self):
        for url, (endpoint_name, args, kwargs) in url_to_endpoint.items():
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            # error is not thrown when queueing, but when executing
            getattr(self.cg, endpoint_name)(*args, **kwargs, qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            with pytest.raises(HTTPError) as HE:
                self.cg.execute_queued()[TEST_ID]
                # If we get past this call, an error was not raised
                print(url)
                print(endpoint_name)
                print(args)
                print(kwargs)

    # ---------- MULTIPLE QUEUED CALLS + SERVER SIDE RATE LIMITING  ----------

    @responses.activate
    def test_multiple_queued(self):
        urls = url_to_endpoint.keys()
        assert len(urls) > 20
        url_qid_map = {url: str(i) for i, url in enumerate(urls)}

        for url in urls:
            responses.add(
                responses.GET,
                url,
                json=self.expected_response[url],
                status=200,
            )

        queued = 0
        for url in urls:
            endpoint_name, args, kwargs = url_to_endpoint[url]
            getattr(self.cg, endpoint_name)(*args, **kwargs, qid=url_qid_map[url])
            queued += 1
            assert len(self.cg._queued_calls) == queued

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0

        for url in urls:
            r = response[url_qid_map[url]]
            if url_to_endpoint[url][0] == "get_global":
                r = {"data": r}
            assert r == self.expected_response[url]

    @responses.activate
    @unittest.mock.patch("pycoingecko_extra.pycoingecko_extra.time.sleep")
    def test_multiple_rate_limited_success(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True

        # Number of calls to make per api endpoint
        num_calls = 7

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

        urls = url_to_endpoint.keys()
        assert len(urls) > 20
        url_qid_map = {url: str(i) for i, url in enumerate(urls)}
        total_calls = num_calls * len(urls)

        for url in urls:
            responses.add_callback(
                responses.GET,
                url,
                callback=callback_stateful(self.expected_response[url]),
                content_type="application/json",
            )

        queued = 0
        for url in urls:
            endpoint_name, args, kwargs = url_to_endpoint[url]
            getattr(self.cg, endpoint_name)(*args, **kwargs, qid=url_qid_map[url])
            queued += 1
            assert len(self.cg._queued_calls) == queued

        self.cg.exp_limit = num_calls
        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == total_calls

        # Each api endpoint call should have num_calls - 1 failures due to rate limiting followed by a single success
        for i in range(0, total_calls):
            is_success = i > 0 and ((i + 1) % num_calls == 0)
            if not is_success:
                assert isinstance(
                    responses.calls[i].response, requests.exceptions.RequestException
                )
                assert responses.calls[i].response.response.status_code == 429
            else:
                assert responses.calls[i].response.status_code == 200

        for url in urls:
            r = response[url_qid_map[url]]
            if url_to_endpoint[url][0] == "get_global":
                r = {"data": r}
            assert r == self.expected_response[url]

    @responses.activate
    @unittest.mock.patch("pycoingecko_extra.pycoingecko_extra.time.sleep")
    def test_multiple_rate_limited_failed(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True

        num_calls = 7

        def request_callback(request):
            raise requests.exceptions.RequestException(
                response=MockResponse(status_code=429)
            )

        urls = url_to_endpoint.keys()
        assert len(urls) > 20
        url_qid_map = {url: str(i) for i, url in enumerate(urls)}

        for url in urls:
            responses.add_callback(
                responses.GET,
                url,
                callback=request_callback,
                content_type="application/json",
            )

        queued = 0
        for url in urls:
            endpoint_name, args, kwargs = url_to_endpoint[url]
            getattr(self.cg, endpoint_name)(*args, **kwargs, qid=url_qid_map[url])
            queued += 1
            assert len(self.cg._queued_calls) == queued

        self.cg.exp_limit = num_calls
        with pytest.raises(Exception) as e:
            self.cg.execute_queued()
        assert str(e.value) == error_msgs["exp_limit_reached"]
        assert len(self.cg._queued_calls) == 0

    # ---------- PAGE RANGE QUERIES ----------

    @responses.activate
    def test_page_range_query_page_start_end(self):
        page_start = 2
        page_end = 4
        npages = page_end - page_start + 1
        purls = self.expected_response_paged.keys()
        url_prefixes = [
            remove_from_querystring(url, ["page", "per_page"]) for url in purls
        ]
        counter = defaultdict(int)
        for url in url_prefixes:
            counter[url] += 1
        assert all([v == npages for v in counter.values()])

        for url in purls:
            responses.add(
                responses.GET, url, json=self.expected_response_paged[url], status=200
            )

        url_prefixes = set(url_prefixes)
        for i, url in enumerate(url_prefixes):
            endpoint_name, args, kwargs = url_to_endpoint[url]
            assert "page" not in kwargs
            getattr(self.cg, endpoint_name)(
                *args,
                **kwargs,
                qid=url,
                page_start=page_start,
                page_end=page_end,
                per_page=5
            )
            assert len(self.cg._queued_calls.keys()) == i + 1
            assert len(self.cg._queued_calls[url]) == npages

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0

        for purl in purls:
            prefix = remove_from_querystring(purl, ["page", "per_page"])
            res = response[prefix]
            page = int(extract_from_querystring(purl, {"page"})["page"])
            pi = page - page_start
            assert self.expected_response_paged[purl] == res[pi]

    @responses.activate
    def test_page_range_query_page_start(self):
        page_start = 2
        page_end = 4
        npages = page_end - page_start + 1
        purls = self.expected_response_paged.keys()
        url_prefixes = [
            remove_from_querystring(url, ["page", "per_page"]) for url in purls
        ]
        counter = defaultdict(int)
        for url in url_prefixes:
            counter[url] += 1
        assert all([v == npages for v in counter.values()])

        def callback_wrapper(data):
            def callback(request):
                return (200, {"Total": "20", "Per-Page": "5"}, json.dumps(data))

            return callback

        for url in purls:
            responses.add_callback(
                responses.GET,
                url,
                callback=callback_wrapper(self.expected_response_paged[url]),
                content_type="application/json",
            )

        url_prefixes = set(url_prefixes)
        for i, url in enumerate(url_prefixes):
            endpoint_name, args, kwargs = url_to_endpoint[url]
            assert "page" not in kwargs
            getattr(self.cg, endpoint_name)(
                *args, **kwargs, qid=url, page_start=page_start, per_page=5
            )
            assert len(self.cg._queued_calls.keys()) == i + 1
            assert len(self.cg._queued_calls[url]) == 1

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0

        for purl in purls:
            prefix = remove_from_querystring(purl, ["page", "per_page"])
            res = response[prefix]
            page = int(extract_from_querystring(purl, {"page"})["page"])
            pi = page - page_start
            assert self.expected_response_paged[purl] == res[pi]
