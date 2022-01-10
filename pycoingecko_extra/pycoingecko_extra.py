import time
import math
import logging
import requests
import inspect
import itertools
from collections import defaultdict
from functools import partial

from pycoingecko import CoinGeckoAPI

# This sets the root logger to write to stdout (your console).
logging.basicConfig()
logger = logging.getLogger("CoinGeckoAPIExtra")

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing _exp_limit. Queued calls are retained."
)


def validate_page_range(page_start, page_end):
    """Validates user supplied values for page_start and page_end"""
    if not page_start:
        raise ValueError("page_end was defined but page_start was not")
    if not (isinstance(page_start, int) and isinstance(page_end, int)):
        raise ValueError(
            f"one or more of page_start: {page_start} or page_end: {page_end} was not an int"
        )
    if page_end < page_start:
        raise ValueError(f"page_end: {page_end} less than page_start: {page_start}")
    if page_start <= 0 or page_end <= 0:
        raise ValueError(
            f"page_start: {page_start} or page_end: {page_end} was less than or equal to 0"
        )


def flatten(data):
    # data should be either a list of lists or a list of dictionaries. it is also non-empty
    d = data[0]
    if isinstance(d, list):
        return list(itertools.chain(*data))
    elif isinstance(d, dict):
        return {k: v for d in data for k, v in d.items()}
    else:
        raise Exception(f"Response of unsupported type: {type(d)}")


class CoinGeckoAPIExtra(CoinGeckoAPI):
    def __init__(self, *args, **kwargs):
        # setup base class normally, removing kwargs specific to the wrapper
        filter_kwargs = ["_exp_limit", "_progress_interval", "_log_level"]
        super().__init__(
            *args, **{k: v for k, v in kwargs.items() if k not in filter_kwargs}
        )
        # ensure we are not overridding any methods on the base class. if this occurs, the method names in the wrapper need to be changed
        members = inspect.getmembers(CoinGeckoAPI, predicate=inspect.isfunction)
        new_methods = set(["execute_queued"])
        overriden_methods = new_methods.intersection(set([m[0] for m in members]))
        if overriden_methods:
            raise Exception(
                f"Wrapper class overwrote existing methods on CoinGeckoAPI class: {overriden_methods}"
            )
        # setup wrapper instance fields, for managing queued calls and rate limit behavior
        self._reset_queued_state()
        self._exp_limit = kwargs.get("_exp_limit", 8)
        self._progress_interval = kwargs.get("_progress_interval", 10)
        logger.setLevel(kwargs.get("_log_level", 20))
        # decorate bound methods on base class that correspond to api calls to enable queueing
        # add page range query support to all functions that support pagination
        # the base api client makes this impossible to dete
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
        for attr in dir(self):
            v = getattr(self, attr)
            if callable(v) and not attr.startswith("_") and attr not in new_methods:
                pagination = attr in paginated_fns
                setattr(self, attr, partial(self._method_queueable, v, pagination))

    def _reset_queued_state(self):
        self._queued_calls = defaultdict(list)
        self._page_range_qids = list()
        self._flatten_qids = list()
        self._infer_page_end_qids = list()

    def _queue_single(self, qid, fn, dup_check, *args, **kwargs):
        if dup_check and qid in self._queued_calls:
            logger.warning(
                f"Warning: multiple calls queued with identical qid: {qid}. Most recent call will overwrite old call."
            )
        self._queued_calls[qid].append((fn, args, kwargs))

    def _execute_queued(self):
        """Execute all queued calls"""
        results = dict()
        progress_updates = 0
        call_count = 0
        for (qid, call_list) in self._queued_calls.items():
            is_page_range_query = qid in self._page_range_qids
            if is_page_range_query:
                results[qid] = list()
            for (fn, args, kwargs) in call_list:
                # make api call (with retries)
                exp = 0
                res = None
                infer_page_end = qid in self._infer_page_end_qids
                # TODO: use infer page end to add more queries to queue after first call is made (parse n per page and total from first response header)
                while res is None and exp < self._exp_limit + 1:
                    try:
                        res = fn(*args, **kwargs)
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
                # determine if we were successful
                if res is None:
                    raise Exception(error_msgs["exp_limit_reached"])
                # store the result in our results cache
                if is_page_range_query:
                    results[qid].append(res)
                else:
                    results[qid] = res
                # log progress
                progress = call_count / len(self._queued_calls) * 100
                if progress > (progress_updates + 1) * self._progress_interval:
                    logger.info(f"Progress: {math.floor(progress)}%")
                    progress_updates += 1
                # increment call counter
                call_count += 1

        # optionally flatten and page range responses if user desires
        for qid in self._queued_calls.keys():
            if qid in self._flatten_qids:
                results[qid] = flatten(results[qid])

        logger.info(f"Progress: 100%")
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
                flat = kwargs.get("_flat")
                if not (page or page_start or page_end) or page:
                    # 1. paged endpoint but no paging arguments specified (api uses default of page 1)
                    # 2. paged endpoint and single page specified (supported by base api client)
                    dup_check = True
                    self._queue_single(qid, fn, dup_check, *args, **kwargs)
                else:
                    # one or more of page_start and page_end is defined
                    validate_page_range(page_start, page_end)
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
                        dup_check = True
                        self._queue_single(
                            qid, fn, dup_check, *args, page=page_start, **kwargs
                        )
                        self._infer_page_end_qids.append(qid)
                    # optionally mark these calls as flattenable
                    if flat:
                        self._flatten_qids.append(qid)
            else:
                # queueable and pagination disabled
                dup_check = True
                self._queue_single(qid, fn, dup_check, *args, **kwargs)
        else:
            return fn(*args, **kwargs)

    def execute_queued(self):
        try:
            results = self._execute_queued()
        except BaseException:
            raise
        finally:
            self._reset_queued_state()
        return results
