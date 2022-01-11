import time
import math
import logging
import requests
import itertools
import json
from typing import List, Set
from collections import defaultdict, deque
from functools import partial
from contextlib import contextmanager

from pycoingecko import CoinGeckoAPI

# This sets the root logger to write to stdout (your console).
logging.basicConfig()
logger = logging.getLogger("CoinGeckoAPIExtra")

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing _exp_limit. Queued calls are retained."
)


class CoinGeckoAPIExtra(CoinGeckoAPI):

    # Base class makes this impossible to determine via introspection so these were manually aggregated
    paginated_fns = [
        # coins
        "get_coins_markets",
        "get_coin_ticker_by_id",
        "get_coin_status_updates_by_id",
        # exchanges
        "get_exchanges_list",
        "get_exchanges_tickers_by_id",
        "get_exchanges_status_updates_by_id",
        # finance
        "get_finance_platforms",
        "get_finance_products",
        # indexes
        "get_indexes",
        # derivatives
        "get_derivatives_exchanges",
        # status
        "get_status_updates",
    ]

    defaults = dict(_exp_limit=8, _progress_interval=10, _log_level=logging.INFO)

    _include_resp = False

    def __init__(self, *args, **kwargs):
        # setup base class normally, removing kwargs specific to the wrapper
        super().__init__(
            *args, **{k: v for k, v in kwargs.items() if k not in self.defaults.keys()}
        )
        # perform instrospection to ensure no overrides of base class, and to get new methods of this subclass
        # we need the list of new methods so we ensure we only decorate methods of base class
        self._detect_overrides()
        new_methods = self._get_new_method_names()
        # setup wrapper instance fields, for managing queued calls, rate limit behavior, pagination
        self._reset_state()
        for k, v in self.defaults.items():
            setattr(self, k, kwargs.get(k) or v)
        logger.setLevel(self._log_level)
        # decorate bound methods on base class that correspond to api calls to enable
        # queueing and page range query support for pagination enabled functions
        for attr in dir(self):
            v = getattr(self, attr)
            if callable(v) and not attr.startswith("_") and attr not in new_methods:
                pagination = attr in self.paginated_fns
                logger.debug(f"Decorating: {attr:60} pagination: {pagination}")
                setattr(self, attr, partial(self._method_queueable, v, pagination))

    def _get_new_method_names(self) -> Set[str]:
        """Returns names of all methods on self that don't exist in parent class"""
        inherited_class = self.__class__.__bases__
        if len(inherited_class) != 1:
            raise ValueError("Parent class introspection broken")
        c = inherited_class[0]
        inherited_methods = set([attr for attr in dir(c) if callable(getattr(c, attr))])
        my_methods = set([attr for attr in dir(self) if callable(getattr(self, attr))])
        return my_methods - inherited_methods

    def _detect_overrides(self, whitelist=set(["_CoinGeckoAPI__request"])) -> None:
        # ensure we are not overridding any methods on the base class. if this occurs, the method names in the wrapper need to be changed
        inherited_class = self.__class__.__bases__
        if len(inherited_class) != 1:
            raise ValueError("Parent class introspection broken")
        cls = inherited_class[0]
        common = cls.__dict__.keys() & self.__class__.__dict__.keys()
        overrides = set(
            m
            for m in common
            if cls.__dict__[m] != self.__class__.__dict__[m] and not m.startswith("__")
        )
        if not all(v in overrides for v in whitelist):
            raise ValueError(
                "Methods whitelisted for override didn't exist on base class"
            )
        overrides = overrides - whitelist
        if overrides:
            raise Exception(
                f"API Client extension overwrote methods in base class: {overrides}"
            )

    def _validate_page_range(self, page_start, page_end) -> None:
        """Validates user supplied values for page_start and page_end"""
        if not page_start:
            raise ValueError("page_start must be defined")
        if not isinstance(page_start, int):
            raise ValueError("page_start must be int")
        if page_end is not None and not isinstance(page_end, int):
            raise ValueError("page_end was specified but was not an int")
        if page_end is not None and page_end < page_start:
            raise ValueError(f"page_end: {page_end} less than page_start: {page_start}")
        if page_start <= 0:
            raise ValueError(f"page_start: {page_start} was less than or equal to 0")
        if page_end is not None and page_end <= 0:
            raise ValueError(f"page_end: {page_end} was less than or equal to 0")

    def _reset_state(self) -> None:
        self._queued_calls = defaultdict(list)
        self._page_range_qids = list()
        self._infer_page_end_qids = list()

    def _queue_single(self, qid, fn, dup_check, *args, **kwargs) -> None:
        if dup_check and qid in self._queued_calls:
            logger.warning(
                f"Warning: multiple calls queued with identical qid: {qid}. Most recent call will overwrite old call."
            )
        self._queued_calls[qid].append((fn, args, kwargs))

    @contextmanager
    def _include_response(self):
        self._include_resp = True
        yield
        self._include_resp = False

    def _CoinGeckoAPI__request(self, url):
        logger.debug(f"HTTPS Request: {url}")
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise
        try:
            response.raise_for_status()
            content = json.loads(response.content.decode("utf-8"))
            if self._include_resp:
                return content, response
            else:
                return content
        except Exception as e:
            try:
                content = json.loads(response.content.decode("utf-8"))
                raise ValueError(content)
            except json.decoder.JSONDecodeError:
                pass
            raise

    def _impute_page_range_calls(self):
        res_cache = dict()
        is_page_range_query = True
        include_response = True
        for qid in self._infer_page_end_qids:
            call_list = self._queued_calls[qid]
            if len(call_list) != 1:
                raise ValueError(
                    "Implementation error. infer_page_end was true but more than one call in call_list"
                )
            fn, args, kwargs = call_list[0]
            page_start = kwargs["page"]
            res, response = self._execute_single(
                {}, is_page_range_query, include_response, qid, fn, *args, **kwargs
            )
            res_cache[(qid, page_start)] = res
            per_page = int(response.headers["Per-Page"])
            total = int(response.headers["Total"])
            page_end = math.ceil(total / per_page)
            # note: we already queued a request for page_start so we begin at page_start + 1
            for page in range(page_start + 1, page_end + 1):
                self._queue_single(qid, fn, False, *args, **{**kwargs, "page": page})
        return res_cache

    def _execute_single(
        self, res_cache, is_page_range_query, include_response, qid, fn, *args, **kwargs
    ):
        exp = 0
        if is_page_range_query:
            res = res_cache.get((qid, kwargs["page"]), None)
        else:
            res = None
        while res is None and exp < self._exp_limit + 1:
            try:
                if include_response:
                    with self._include_response():
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
        if exp == self._exp_limit + 1:
            raise Exception(error_msgs["exp_limit_reached"])
        return res

    def _execute_queued(self):
        """Execute all queued calls"""
        # impute calls related to page range queries where page_end is not specified
        res_cache = self._impute_page_range_calls()
        # execute all queued calls
        results = {qid: list() for qid in self._page_range_qids}
        last_progress = 0
        call_count = 0
        num_calls = sum([len(v) for v in self._queued_calls.values()])
        include_response = False
        for (qid, call_list) in self._queued_calls.items():
            call_list = deque(call_list)
            is_page_range_query = qid in self._page_range_qids
            for fn, args, kwargs in call_list:
                # make api call (with retries)
                res = self._execute_single(
                    res_cache,
                    is_page_range_query,
                    include_response,
                    qid,
                    fn,
                    *args,
                    **kwargs,
                )
                # store the result in our results cache
                if is_page_range_query:
                    results[qid].append(res)
                else:
                    results[qid] = res
                # log progress
                call_count += 1
                progress = call_count / num_calls * 100
                next_progress = last_progress + self._progress_interval
                if progress >= next_progress:
                    logger.info(f"Progress: {math.floor(progress)}%")
                    last_progress = progress
        return results

    def _method_queueable(self, fn, pagination, *args, **kwargs):
        """Runs method normally is 'qid' not in kwargs. Queues method call for later execution if 'qid' in kwargs"""
        qid = kwargs.get("qid")
        if qid:
            try:
                qid = str(qid)
            except:
                raise ValueError(f"Could not coerce qid to string")
            del kwargs["qid"]
            if pagination:
                page = kwargs.get("page")
                page_start = kwargs.get("_page_start")
                page_end = kwargs.get("_page_end")
                for k in ["_page_start", "_page_end"]:
                    if k in kwargs:
                        del kwargs[k]
                if not (page or page_start or page_end) or page:
                    # 1. paged endpoint but no paging arguments specified (api uses default of page 1)
                    # 2. paged endpoint and single page specified (supported by base api client)
                    self._queue_single(qid, fn, True, *args, **kwargs)
                else:
                    # one or more of page_start and page_end is defined
                    self._validate_page_range(page_start, page_end)
                    # mark this qid as representing a page range query
                    self._page_range_qids.append(qid)
                    # queue a single call per page in range
                    if page_end:
                        for i, page in enumerate(range(page_start, page_end + 1)):
                            # all queued requests after first are allowed to have same qid, as they are part of a page range query
                            dup_check = i == 0
                            self._queue_single(
                                qid, fn, dup_check, *args, page=page, **kwargs
                            )
                    else:
                        # when only page_start is specified, we want to queue a request for all available pages
                        # this can only be determined at execution time so we queue a single request now and the
                        # rest will be queued as a part of execute_many
                        self._queue_single(
                            qid, fn, True, *args, page=page_start, **kwargs
                        )
                        self._infer_page_end_qids.append(qid)
            else:
                # queueable and pagination disabled
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
