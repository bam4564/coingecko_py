import time
import math
import logging
import requests
import inspect
from functools import partial
from pycoingecko import CoinGeckoAPI

logger = logging.getLogger("CoinGeckoAPIExtra")

logger.setLevel(50)

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing _exp_limit. Queued calls are retained."
)


def method_queueable(self, fn, *args, **kwargs):
    """Runs method normally is 'qid' not in kwargs. Queues method call for later execution if 'qid' in kwargs"""
    qid = kwargs.get("qid")
    if qid:
        del kwargs["qid"]
        if qid in self._queued_calls:
            logger.warning(
                f"Warning: multiple calls queued with identical qid: {qid}. Most recent call will overwrite old call."
            )
        self._queued_calls[qid] = (fn, args, kwargs)
    else:
        return fn(*args, **kwargs)


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
        self._queued_calls = dict()
        self._exp_limit = kwargs.get("_exp_limit", 8)
        self._progress_interval = kwargs.get("_progress_interval", 10)
        logger.setLevel(kwargs.get("_log_level", 20))
        # decorate bound methods on base class that correspond to api calls to enable queueing
        for attr in dir(self):
            v = getattr(self, attr)
            if callable(v) and not attr.startswith("_") and attr not in new_methods:
                setattr(self, attr, partial(method_queueable, self, v))

    def execute_queued(self):
        """Generic implementation of exponential backoff for sequence of calls to coingecko api to deal with rate limiting
        Logs progress updates (percentage of calls completed) at configurable intervals
        """
        results = dict()
        progress_updates = 0
        for i, ((qid), (fn, args, kwargs)) in enumerate(self._queued_calls.items()):
            exp = 0
            while results.get(qid) is None and exp < self._exp_limit + 1:
                try:
                    results[qid] = fn(*args, **kwargs)
                except requests.exceptions.ConnectionError as e:
                    # this is a subclass of requests.exceptions.RequestException that is a failure condition
                    raise e
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
            progress = i / len(self._queued_calls) * 100
            if progress > (progress_updates + 1) * self._progress_interval:
                logger.info(f"Progress: {math.floor(progress)}%")
                progress_updates += 1
        logger.info(f"Progress: 100%")
        # reset the call queue
        self._queued_calls = dict()
        return results
