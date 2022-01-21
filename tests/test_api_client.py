import math
import json
import pytest
import unittest
import requests
import responses
from typing import Callable
from collections import Counter
from requests.exceptions import HTTPError

from coingecko_py import CoingeckoApi, error_msgs
from coingecko_py.utils.api_meta import api_meta
from coingecko_py.utils.utils import (
    extract_from_querystring,
    sort_querystring,
    update_querystring,
    without_keys,
)

TEST_ID = "TESTING_ID"
TEST_API_KEY = "dummy_key"
TIME_PATCH_PATH = "coingecko_py.coingecko_py.time.sleep"


@pytest.fixture(scope="class", autouse=True)
def cg(request):
    request.cls.cg = CoingeckoApi(log_level=10)


@pytest.fixture(scope="class", autouse=True)
def cg_pro(request):
    request.cls.cg_pro = CoingeckoApi(log_level=10, api_key=TEST_API_KEY)


@pytest.fixture(scope="class")
def calls(request):
    cg = request.cls.cg
    url_to_method = api_meta.get_url_to_method()
    expected_response = api_meta.get_test_api_responses()
    test_api_calls = api_meta.get_test_api_calls()
    calls = list()
    for url_template, method_name in url_to_method.items():
        expected = expected_response[url_template]
        assert expected
        test_call = test_api_calls[url_template]
        path_args = test_call["path"]
        query_args = test_call["query"]
        url = api_meta.materialize_url_template(url_template, path_args, query_args)
        args, kwargs = api_meta.transform_path_query_to_args_kwargs(
            url_template, path_args, query_args
        )
        fn = getattr(cg, method_name)
        calls.append((url, expected, fn, method_name, args, kwargs))
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


@pytest.mark.usefixtures("cg")
@pytest.mark.usefixtures("cg_pro")
@pytest.mark.usefixtures("calls")
class TestApiClient(unittest.TestCase):

    # ------------ TEST UTILS ----------------------
    @pytest.mark.skip
    def _assert_urls_call_count(self, expected_urls, responses):
        """Asserts that the expected set of requested urls matches the actual set of
        requested urls. Performs normalization on url querystrings so order of
        query string params between compared urls does not matter.
        """
        counter = Counter([sort_querystring(url) for url in expected_urls])
        actual_call_counter = Counter()
        for c in responses.calls:
            actual_call_counter[sort_querystring(c.request.url)] += 1
        assert counter == actual_call_counter

    @pytest.mark.skip
    def test_decode_failure(
        self,
        queued: bool,
        callback: Callable,
        ErrorClass: BaseException,
        msg_match: str,
        responses,
    ):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            responses.add_callback(responses.GET, url, callback)
            expected_urls.append(url)
            if not queued:
                with pytest.raises(ErrorClass) as exc_info:
                    fn(*args, **kwargs)
            else:
                fn(*args, **kwargs, qid=str(i))
                with pytest.raises(ErrorClass) as exc_info:
                    self.cg.execute_queued()
            assert exc_info.value.strerror == msg_match
            assert isinstance(exc_info.value.response, requests.Response)
            assert exc_info.value.response.status_code == 200
        self._assert_urls_call_count(expected_urls, responses)

    # ------------ TEST CONNECTION ERROR (Normal + Queued) ----------------------
    # No endpoint match for outgoing requests

    @responses.activate
    def test_connection_error(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            expected_urls.append(url)
            with pytest.raises(requests.exceptions.ConnectionError):
                fn(*args, **kwargs)
        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    def test_connection_error_queued(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            expected_urls.append(url)
            fn(*args, **kwargs, qid=str(i))
            assert len(self.cg._queued_calls) == 1
            with pytest.raises(requests.exceptions.ConnectionError):
                self.cg.execute_queued()
        self._assert_urls_call_count(expected_urls, responses)

    # ------------ TEST FAILED RESPONSE CODE (Normal + Queued) ----------------------
    # Response code is not 200

    @responses.activate
    def test_failed(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            expected_urls.append(url)
            with pytest.raises(HTTPError) as exc_info:
                fn(*args, **kwargs)
            assert isinstance(exc_info.value.response, requests.Response)
            assert exc_info.value.response.status_code == 404
        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    def test_failed_queued(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                status=404,
            )
            expected_urls.append(url)
            fn(*args, **kwargs, qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            with pytest.raises(HTTPError) as exc_info:
                self.cg.execute_queued()
            assert isinstance(exc_info.value.response, requests.Response)
            assert exc_info.value.response.status_code == 404
            assert len(self.cg._queued_calls) == 0
        self._assert_urls_call_count(expected_urls, responses)

    # ------------ TEST FAILED DECODING (Normal + Queued) ----------------------
    # Content returned from in response is either not byte decodable or json decodable

    @responses.activate
    def test_failed_body_json_decode(self):
        queued = False
        response_callback = lambda request: (200, {}, "{'one': 2,}")
        ErrorClass = requests.exceptions.JSONDecodeError
        msg_match = error_msgs["failed_decode_json"]
        self.test_decode_failure(
            queued, response_callback, ErrorClass, msg_match, responses
        )

    @responses.activate
    def test_failed_body_json_decode_queued(self):
        queued = True
        response_callback = lambda request: (200, {}, "{'one': 2,}")
        ErrorClass = requests.exceptions.JSONDecodeError
        msg_match = error_msgs["failed_decode_json"]
        self.test_decode_failure(
            queued, response_callback, ErrorClass, msg_match, responses
        )

    @responses.activate
    def test_failed_body_byte_decode(self):
        queued = False
        response_callback = lambda request: (200, {}, b"\x00\xaa\xff")
        ErrorClass = requests.exceptions.ContentDecodingError
        msg_match = error_msgs["failed_decode_bytes"]
        self.test_decode_failure(
            queued, response_callback, ErrorClass, msg_match, responses
        )

    @responses.activate
    def test_failed_body_byte_decode_queued(self):
        queued = True
        response_callback = lambda request: (200, {}, b"\x00\xaa\xff")
        ErrorClass = requests.exceptions.ContentDecodingError
        msg_match = error_msgs["failed_decode_bytes"]
        self.test_decode_failure(
            queued, response_callback, ErrorClass, msg_match, responses
        )

    # ------------ TEST API ENDPOINTS SUCCESS / FAILURE (Normal + Queued) ----------------------

    @responses.activate
    def test_success(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            expected_urls.append(url)
            response = fn(*args, **kwargs)
            assert response == expected
        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    def test_success_queued(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            expected_urls.append(url)
            fn(*args, **kwargs, qid=TEST_ID)
            assert len(self.cg._queued_calls) == 1
            response = self.cg.execute_queued()[TEST_ID]
            assert len(self.cg._queued_calls) == 0
            assert response == expected
        self._assert_urls_call_count(expected_urls, responses)

    # ---------- MULTIPLE QUEUED CALLS + SERVER SIDE RATE LIMITING  ----------

    @responses.activate
    def test_multiple_queued(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            expected_urls.append(url)
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == len(self.calls)

        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            assert response[qid] == expected

        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    @unittest.mock.patch(TIME_PATCH_PATH)
    def test_multiple_rate_limited_success(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True
        calls = list(self.calls)
        num_attempts = 3
        total_calls = len(calls) * num_attempts

        # queue calls
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            server = FailThenSuccessServer(num_attempts, expected)
            responses.add_callback(
                responses.GET,
                url,
                callback=getattr(server, "request_callback"),
                content_type="application/json",
            )
            expected_urls = expected_urls + [url] * num_attempts
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        # execute calls
        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == total_calls

        # validate expected
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
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

        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    @unittest.mock.patch(TIME_PATCH_PATH)
    def test_multiple_rate_limited_failed(self, sleep_patch):
        # patch time.sleep in the imported module so it doesn't block test
        sleep_patch.return_value = True
        self.cg.exp_limit = 2
        rate_limit_count = 10
        total_calls = rate_limit_count + self.cg.exp_limit
        server = SuccessThenFailServer(rate_limit_count)

        # queue calls
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            responses.add_callback(
                responses.GET,
                url,
                callback=getattr(server, "request_callback"),
                content_type="application/json",
            )
            # first rate_limit_count - 1 calls will succeed
            # subsequent self.cg.exp_limit + 1 calls will be rate limited
            # client will stop sending requests at this point as it hit exp_limit
            if i < rate_limit_count - 1:
                expected_urls.append(url)
            elif i == rate_limit_count - 1:
                expected_urls = expected_urls + [url] * (self.cg.exp_limit + 1)
            fn(*args, **kwargs, qid=qid)
            assert len(self.cg._queued_calls) == i + 1
            assert len(responses.calls) == 0

        # execute calls
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

        self._assert_urls_call_count(expected_urls, responses)

    # ---------- PAGE RANGE QUERIES ----------

    @responses.activate
    def test_page_range_query_bounded(self):
        paginated_method_names = set(api_meta.get_paginated_method_names())
        page_start = 1
        page_end = 3
        num_pages = page_end - page_start + 1
        expected_paged = dict()
        queued = 0
        expected_urls = []
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            name = fn.__name__
            if name in paginated_method_names:
                paginated_method_names.remove(name)
                qparams = extract_from_querystring(url, ["page"])
                assert "page" in qparams
                # add a response for all urls that will be queried within the page range
                expected_paged[qid] = list()
                for new_page in range(page_start, page_end + 1):
                    url_paged = update_querystring(url, dict(page=new_page))
                    expected_paged[qid].append([new_page, expected])
                    expected_urls.append(url_paged)
                    responses.add(
                        responses.GET,
                        url_paged,
                        json=expected_paged[qid][-1],
                        status=200,
                    )
                # queue a single page range query
                new_kwargs = without_keys(kwargs, "page")
                fn(
                    *args,
                    **new_kwargs,
                    qid=qid,
                    page_start=page_start,
                    page_end=page_end
                )
                queued += 1
                assert len(self.cg._queued_calls) == queued
                assert len(responses.calls) == 0

        # ensure we queued a test call for all paginated methods
        assert len(paginated_method_names) == 0

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == queued * num_pages

        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            name = fn.__name__
            if name in paginated_method_names:
                assert expected_paged[qid] == response[qid]

        self._assert_urls_call_count(expected_urls, responses)

    @responses.activate
    def test_page_range_query_unbounded(self):
        paginated_method_names = set(api_meta.get_paginated_method_names())
        page_start = 1
        per_page = 5
        total = 19
        num_pages = math.ceil(total / per_page)
        page_end = (
            page_start + num_pages - 1
        )  # note, we won't pass page_end to the function call. this represents the mocked end of pages
        expected_paged = dict()
        queued = 0
        expected_urls = []

        def callback_wrapper(data):
            def callback(request):
                return (
                    200,
                    {"Total": str(total), "Per-Page": str(per_page)},
                    json.dumps(data),
                )

            return callback

        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            name = fn.__name__
            if name in paginated_method_names:
                paginated_method_names.remove(name)
                qparams = extract_from_querystring(url, ["page"])
                assert "page" in qparams
                # add a response for all urls that will be queried within the page range
                expected_paged[qid] = list()
                for new_page in range(page_start, page_end + 1):
                    url_paged = update_querystring(
                        url, dict(page=new_page, per_page=per_page)
                    )
                    expected_paged[qid].append([new_page, expected])
                    expected_urls.append(url_paged)
                    responses.add_callback(
                        responses.GET,
                        url_paged,
                        callback=callback_wrapper(expected_paged[qid][-1]),
                        content_type="application/json",
                    )
                # queue a single unbounded page range query
                new_kwargs = without_keys(kwargs, "page")
                new_kwargs["per_page"] = per_page
                fn(
                    *args, **new_kwargs, qid=qid, page_start=page_start
                )  # IMPORTANT: page_end omitted
                queued += 1
                assert len(self.cg._queued_calls) == queued
                assert len(responses.calls) == 0

        # ensure we queued a test call for all paginated methods
        assert len(paginated_method_names) == 0

        response = self.cg.execute_queued()
        assert len(self.cg._queued_calls) == 0
        assert len(responses.calls) == queued * num_pages

        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            qid = str(i)
            name = fn.__name__
            if name in paginated_method_names:
                assert expected_paged[qid] == response[qid]

        self._assert_urls_call_count(expected_urls, responses)

    def test_validate_page_range(self):
        with pytest.raises(
            ValueError, match=error_msgs["page_start_undefined"]
        ) as exc_info:
            self.cg._validate_page_range(None, None)
        with pytest.raises(
            ValueError, match=error_msgs["page_start_not_int"]
        ) as exc_info:
            self.cg._validate_page_range("5", 6)
        with pytest.raises(
            ValueError, match=error_msgs["page_end_not_int"]
        ) as exc_info:
            self.cg._validate_page_range(5, "6")
        with pytest.raises(
            ValueError, match=error_msgs["page_end_before_page_start"]
        ) as exc_info:
            self.cg._validate_page_range(5, 4)
        with pytest.raises(
            ValueError, match=error_msgs["page_start_lte_zero"]
        ) as exc_info:
            self.cg._validate_page_range(0, 3)

    # ---------- PRO USER API AUTHENTICATION ----------

    @responses.activate
    def test_success_pro_authentication(self):
        expected_urls = list()
        for i, (url, expected, fn, method_name, args, kwargs) in enumerate(self.calls):
            # update querystring to contain api key
            url = update_querystring(url, dict(x_cg_pro_api_key=TEST_API_KEY))
            responses.add(
                responses.GET,
                url,
                json=expected,
                status=200,
            )
            expected_urls.append(url)
            # get method from client initialized with pro api key
            fn = getattr(self.cg_pro, method_name)
            response = fn(*args, **kwargs)
            assert response == expected
        self._assert_urls_call_count(expected_urls, responses)
