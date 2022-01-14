from collections import defaultdict
import contextlib
import json
import pytest
import unittest
import requests
import responses
from functools import partial
from copy import copy
from requests.exceptions import HTTPError

# from pycoingecko_extra.utils import extract_from_querystring, remove_from_querystring
from scripts.utils import materialize_url_template
from scripts.swagger import get_parameters
from pycoingecko_extra import CoinGeckoAPI, error_msgs

TEST_ID = "TESTING_ID"
TIME_PATH = "pycoingecko_extra.pycoingecko_v2.time.sleep"


@pytest.fixture(scope="class", autouse=True)
def cg(request):
    request.cls.cg = CoinGeckoAPI(log_level=10)


@pytest.fixture(scope="class")
def calls(request, cg):
    with open("data/test_api_responses.json", "r") as f:
        expected_response = json.loads(f.read())
    with open("data/url_to_method.json", "r") as f:
        url_to_method = json.loads(f.read())
    with open("data/test_api_calls.json", "r") as f:
        test_api_calls = json.loads(f.read())
    calls = list()
    for url_template, method_name in url_to_method.items():
        expected = expected_response[url_template]
        assert expected
        test_call = test_api_calls[url_template]
        args = test_call["args"]
        kwargs = test_call["kwargs"]
        url = materialize_url_template(url_template, args, kwargs)
        args, kwargs = transform_args_kwargs(url_template, args, kwargs)
        fn = getattr(request.cls.cg, method_name)
        calls.append((url, expected, fn, args, kwargs))
    request.cls.calls = calls


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class SuccessThenFailServer:
    """first limit - 1 calls ---> 200 (empty body)
    subsequent calls ---> 429
    """

    def __init__(self, limit):
        self.calls = 0
        self.limit = limit

    def request_callback(self, request):
        self.calls += 1
        if self.calls < self.limit:
            return (200, {}, "{}")
        else:
            raise requests.exceptions.RequestException(
                response=MockResponse(status_code=429)
            )


class FailThenSuccessServer:
    """first limit - 1 calls ---> 429 (data body)
    subsequent calls ---> 200
    """

    def __init__(self, limit, data):
        self.calls = 0
        self.limit = limit
        self.data = data

    def request_callback(self, request):
        self.calls += 1
        if self.calls >= self.limit:
            return (200, {}, json.dumps(self.data))
        else:
            raise requests.exceptions.RequestException(
                response=MockResponse(status_code=429)
            )


def transform_args_kwargs(url_template, args, kwargs):
    """args and kwargs from input were used to materize url template
    this function transforms them to be supplied to API client endpoint function
    """
    args = copy(args)
    kwargs = copy(kwargs)
    params = get_parameters(url_template)
    for p in params:
        if p["required"] and p["in"] == "query":
            name = p["name"]
            args.append(kwargs[name])
            del kwargs[name]
    return args, kwargs


@pytest.mark.usefixtures("cg")
@pytest.mark.usefixtures("calls")
class TestWrapper(unittest.TestCase):

    # ------------ TEST CONNECTION FAILED (Normal + Queued) ----------------------

    @responses.activate
    def test_connection_error_normal(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.ping_get()

    @responses.activate
    def test_connection_error_queued(self):
        self.cg.ping_get(qid=TEST_ID)
        assert len(self.cg._queued_calls) == 1
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cg.execute_queued()

    # ------------ TEST API ENDPOINTS SUCCESS / FAILURE (Normal + Queued) ----------------------

    @responses.activate
    def test_success_normal(self):
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            response = fn(*args, **kwargs)
            assert len(responses.calls) == i + 1
            assert response == expected

    @responses.activate
    def test_failed_normal(self):
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            with pytest.raises(HTTPError) as HE:
                fn(*args, **kwargs)
            assert len(responses.calls) == i + 1

    @responses.activate
    def test_success_queued(self):
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            fn(*args, **kwargs, qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            response = self.cg.execute_queued()[TEST_ID]
            assert len(self.cg._queued_calls) == 0
            assert len(responses.calls) == i + 1
            assert response == expected

    @responses.activate
    def test_failed_queued(self):
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            fn(*args, **kwargs, qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            with pytest.raises(HTTPError) as HE:
                self.cg.execute_queued()
            assert len(self.cg._queued_calls) == 0
            assert len(responses.calls) == i + 1

    # ---------- MULTIPLE QUEUED CALLS + SERVER SIDE RATE LIMITING  ----------

    @responses.activate
    def test_multiple_queued(self):
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == len(self.calls)

        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            assert response[qid] == expected

    @responses.activate
    @unittest.mock.patch(TIME_PATH)
    def test_multiple_rate_limited_success(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True
        calls = list(self.calls)
        num_attempts = 3
        total_calls = len(calls) * num_attempts

        # queue calls
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            server = FailThenSuccessServer(num_attempts, expected)
            responses.add_callback(
                responses.GET,
                url,
                callback=getattr(server, "request_callback"),
                content_type="application/json",
            )
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        # execute calls
        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == total_calls

        # validate expected
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            assert response[qid] == expected

        # validate rate limiting
        for i in range(0, total_calls):
            is_success = i > 0 and ((i + 1) % num_attempts == 0)
            if not is_success:
                assert isinstance(
                    responses.calls[i].response, requests.exceptions.RequestException
                )
                assert responses.calls[i].response.response.status_code == 429
            else:
                assert responses.calls[i].response.status_code == 200

    @responses.activate
    @unittest.mock.patch(TIME_PATH)
    def test_multiple_rate_limited_failed(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True
        self.cg.exp_limit = 2
        rate_limit_count = 10
        server = SuccessThenFailServer(rate_limit_count)

        # queue calls
        for i, (url, expected, fn, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            responses.add_callback(
                responses.GET,
                url,
                callback=getattr(server, "request_callback"),
                content_type="application/json",
            )
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        # execute calls
        # first rate_limit_count - 1 calls will succeed
        # subsequent self.cg.exp_limit + 1 calls will be rate limited
        # client will stop sending requests at this point as it hit exp_limit
        total_calls = rate_limit_count + self.cg.exp_limit
        with pytest.raises(Exception) as e:
            self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == total_calls
        assert str(e.value) == error_msgs["exp_limit_reached"]

        # validate rate limiting
        for i in range(0, total_calls):
            if i + 1 < rate_limit_count:
                assert responses.calls[i].response.status_code == 200
            else:
                assert isinstance(
                    responses.calls[i].response, requests.exceptions.RequestException
                )
                assert responses.calls[i].response.response.status_code == 429
