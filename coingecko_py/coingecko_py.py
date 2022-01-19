import time
import math
import logging
import json
import requests
from collections import defaultdict
from functools import partial
from contextlib import contextmanager
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

from coingecko_py.swagger_generated.swagger_client import (
    ApiClient as ApiClientSwagger,
    CoingeckoApi as CoinGeckoApiSwagger,
)

from coingecko_py.utils.utils import without_keys, dict_get
from coingecko_py.utils.api_meta import api_meta


logging.basicConfig()
logger = logging.getLogger(__name__)

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing exp_limit. Queued calls are retained.",
    failed_decode_bytes="Unable to decode bytes to utf-8 string",
    failed_decode_json="Unable to decode json from string",
    page_start_undefined="page_start must be defined",
    page_start_not_int="page_start must be int",
    page_end_not_int="page_end was specified but was not an int",
    page_end_before_page_start=r"page_end: \d+ less than page_start: \d+",
    page_start_lte_zero=r"page_start: \d+ was less than or equal to 0",
)


class CoingeckoApiClient(ApiClientSwagger):
    def __init__(self):
        super().__init__()
        # setup HTTP session
        # TODO: compare benefits of session vs pool
        self.request_timeout = 120
        self.session = requests.Session()
        self.scheme = "https"
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount(f"{self.scheme}://", HTTPAdapter(max_retries=retries))
        self._include_response = False

    @contextmanager
    def request_with_response(self):
        """Context manager that allows for chaning the return value structure of api calls when necessary

        The main use case for this is for page range queries, where we need the raw response object to
        be returned from the api client.
        """
        self._include_response = True
        yield
        self._include_response = False

    def call_api(
        self, resource_path, method, path_params, query_params, header_params, **kwargs
    ):
        path_args = list(
            path_params.values()
        )  # dictionaries are ordered from python 3.6 on so this is fine.
        query_args = {v[0]: v[1] for v in query_params}
        url = api_meta.materialize_url_template(resource_path, path_args, query_args)
        logger.debug(f"{self.scheme} request: {url}")
        assert method == "GET"

        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.info(
                f"{self.scheme} response had failure status code: {e.response.status_code}"
            )
            raise e

        try:
            content = json.loads(response.content.decode("utf-8", "strict"))
        except UnicodeDecodeError:
            raise requests.exceptions.ContentDecodingError(
                0, error_msgs["failed_decode_bytes"], response=response
            )
        except json.decoder.JSONDecodeError:
            raise requests.exceptions.JSONDecodeError(
                0, error_msgs["failed_decode_json"], response=response
            )

        if self._include_response:
            return content, response
        else:
            return content


class ResultsCache:
    def __init__(self):
        self.cache = dict()
        self.page_range_query_first_call_keys = set()

    def put_page_range_unbounded_first_result(self, qid, page, data):
        assert page is not None
        self.page_range_query_first_call_keys.add((page, qid))
        self.put_page_range_query(qid, data)

    def check_contains_page_range_unbounded_first_result(self, qid, page):
        return (page, qid) in self.page_range_query_first_call_keys

    def put(self, qid, data):
        self.cache[qid] = data

    def put_page_range_query(self, qid, data):
        if qid not in self.cache:
            self.cache[qid] = list()
        self.cache[qid].append(data)

    def data(self):
        return self.cache


class CoingeckoApi(CoinGeckoApiSwagger):

    defaults = dict(exp_limit=8, progress_interval=10, log_level=logging.INFO)

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            api_client=CoingeckoApiClient(),
            **without_keys(kwargs, *self.defaults.keys()),
        )
        # setup wrapper instance fields, for managing queued calls, rate limit behavior, page range queries
        self._reset_state()
        for k, v in self.defaults.items():
            setattr(self, k, kwargs.get(k) or v)
        logger.setLevel(self.log_level)
        # decorate bound methods on base class that correspond to api calls to enable
        # queueing and page range query support for page range query enabled functions
        method_names = api_meta.get_api_method_names()
        paginated_method_names = api_meta.get_paginated_method_names()
        for name in method_names:
            v = getattr(self, name)
            page_range_query = name in paginated_method_names
            logger.debug(f"Decorating: {name:60} page_range_query: {page_range_query}")
            setattr(self, name, partial(self._wrap_api_endpoint, v, page_range_query))

    def _validate_page_range(self, page_start, page_end) -> None:
        """Validates user supplied values for page_start and page_end"""
        if page_start is None:
            raise ValueError(error_msgs["page_start_undefined"])
        if not isinstance(page_start, int):
            raise ValueError(error_msgs["page_start_not_int"])
        if page_end is not None and not isinstance(page_end, int):
            raise ValueError(error_msgs["page_end_not_int"])
        if page_end is not None and page_end < page_start:
            raise ValueError(f"page_end: {page_end} less than page_start: {page_start}")
        if page_start <= 0:
            raise ValueError(f"page_start: {page_start} was less than or equal to 0")

    def _reset_state(self) -> None:
        """Resets internal state. State is used to support queueing and page range queries"""
        self._queued_calls = defaultdict(list)
        self._page_range_qids = list()
        self._infer_page_end_qids = list()
        logger.debug("Resetting state")

    def _queue_single(self, qid, fn, dup_check, *args, **kwargs) -> None:
        """Queue a single API call. Optionally perform a duplicate check to see if qid is being overwritten"""
        if dup_check and qid in self._queued_calls:
            # TODO: Test that this log appears when queueing two calls with same qid
            logger.warning(
                f"Warning: multiple calls queued with identical qid: {qid}. Most recent call will overwrite old call."
            )
        self._queued_calls[qid].append((fn, args, kwargs))

    def _impute_page_range_calls(self, res_cache: ResultsCache):
        """Finds each queued call that is a page range query where page_start is defined and page_end is not included.
        Executes each of these calls to get an HTTP header back containing information on how many pages exist. With
        this information, we queue the remainder of calls. We cache the result of the call we already executed in
        res_cache and return this value.
        """
        include_response = True
        for qid in self._infer_page_end_qids:
            call_list = self._queued_calls[qid]
            if len(call_list) != 1:
                raise ValueError(
                    "Implementation error. infer page_end was true but more than one call in call_list"
                )
            fn, args, kwargs = call_list[0]
            page_start = kwargs["page"]
            res, response = self._execute_single(include_response, fn, *args, **kwargs)
            res_cache.put_page_range_unbounded_first_result(qid, page_start, res)
            per_page = int(response.headers["Per-Page"])
            total = int(response.headers["Total"])
            page_end = math.ceil(total / per_page)
            logger.debug(
                f"page range query: {qid} page_start: {page_start:4} page_end: {page_end:4} per_page: {per_page:4} total: {total}"
            )
            # note: we already queued a request for page_start so we begin at page_start + 1
            for page in range(page_start + 1, page_end + 1):
                logger.debug(f"queueing page: {page}")
                self._queue_single(qid, fn, False, *args, **{**kwargs, "page": page})

    def _execute_single(self, include_response, fn, *args, **kwargs):
        """Execute a single API call with exponential backoff retries to deal with server side rate limiting.

        Maximum of exp_limit + 1 request attempts.
        """
        exp = 0
        res = None
        while exp < self.exp_limit + 1:
            try:
                if include_response:
                    with self.api_client.request_with_response():
                        res, response = fn(*args, **kwargs)
                    return res, response
                else:
                    res = fn(*args, **kwargs)
                    return res
            except requests.exceptions.ConnectionError:
                # this is a subclass of requests.exceptions.RequestException that is a failure condition
                raise
            except requests.exceptions.RequestException as e:
                if e.response.status_code == RATE_LIMIT_STATUS_CODE:
                    secs = 2 ** exp
                    logger.info(f"Rate limited: sleeping {secs} seconds")
                    time.sleep(secs)
                    exp += 1
                else:
                    # Any non 429 http respose error code is a failure condition
                    raise e
        if exp == self.exp_limit + 1:
            raise Exception(error_msgs["exp_limit_reached"])
        return res

    def _execute_queued(self):
        """Execute all queued calls

        - Prior to execution, we impute calls for page range queries
        - Logs progress at configurable intervals
        """
        # impute calls related to page range queries where page_end is not specified
        cache = ResultsCache()
        self._impute_page_range_calls(cache)
        # execute all queued calls
        last_progress = 0
        call_count = 0
        # TODO: this value is slightly off. should include number of page range calls
        #       executed when imputing page range calls
        num_calls = sum([len(v) for v in self._queued_calls.values()])
        include_response = False
        logger.info(f"Begin executing {num_calls} queued calls")
        for (qid, call_list) in self._queued_calls.items():
            for fn, args, kwargs in call_list:
                # check if this call was already completed (first call in unbounded page range query)
                if cache.check_contains_page_range_unbounded_first_result(
                    qid, kwargs.get("page", None)
                ):
                    continue
                # if cache miss, make api call (with retries)
                res = self._execute_single(
                    include_response,
                    fn,
                    *args,
                    **kwargs,
                )
                # store the result
                if qid in self._page_range_qids:
                    cache.put_page_range_query(qid, res)
                else:
                    cache.put(qid, res)
                # log progress
                call_count += 1
                progress = call_count / num_calls * 100
                next_progress = last_progress + self.progress_interval
                if progress >= next_progress:
                    logger.info(f"Progress: {math.floor(progress)}%")
                    last_progress = progress
        return cache.data()

    def _queue_page_range_query(self, qid, fn, *args, **kwargs) -> None:
        page, page_start, page_end = dict_get(kwargs, "page", "page_start", "page_end")
        kwargs = without_keys(kwargs, "page_start", "page_end")
        if not (page or page_start or page_end) or page:
            # 1. paged endpoint but no paging arguments specified (api uses default of page 1)
            # 2. paged endpoint and single page specified (supported by base api client)
            self._queue_single(qid, fn, True, *args, **kwargs)
        else:
            # one or more of page_start and page_end is defined ---> is page range query
            self._validate_page_range(page_start, page_end)
            self._page_range_qids.append(qid)
            if page_end:
                for i, page in enumerate(range(page_start, page_end + 1)):
                    # all queued requests after first are allowed to have same qid, as they are part of a page range query
                    dup_check = i == 0
                    self._queue_single(qid, fn, dup_check, *args, page=page, **kwargs)
            else:
                # when only page_start is specified we are dealing with an unbounded page range query.
                # the total number of queries can only be determined at execution time. we queue first
                # now and the rest will be queued and executed when `execute_many` is called
                self._queue_single(qid, fn, True, *args, page=page_start, **kwargs)
                self._infer_page_end_qids.append(qid)

    def _wrap_api_endpoint(self, fn, page_range_query, *args, **kwargs):
        """Decorator that will be applied to all API endpoints on base class.

        Adds support for method queueing and page range queries.
        """
        qid = kwargs.get("qid")
        if qid:
            qid = str(qid)
            kwargs = without_keys(kwargs, "qid")
            if page_range_query:
                self._queue_page_range_query(qid, fn, *args, **kwargs)
            else:
                self._queue_single(qid, fn, True, *args, **kwargs)
        else:
            return fn(*args, **kwargs)

    def execute_queued(self):
        try:
            results = self._execute_queued()
        except BaseException:
            raise
        finally:
            self._reset_state()
        return results
