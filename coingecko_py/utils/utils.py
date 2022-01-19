from typing import List
from collections import OrderedDict
from contextlib import contextmanager
import urllib.parse as urlparse
from urllib.parse import urlencode, urlunparse


def without_keys(d: dict, *rm_keys):
    """Returns copy of dictionary with each key in rm_keys removed"""
    return {k: v for k, v in d.items() if k not in rm_keys}


def with_keys(d: dict, *keep_keys):
    """Returns copy of dictionary with each key in keep_keys retained"""
    return {k: v for k, v in d.items() if k in keep_keys}


def update_querystring(url: str, params: dict):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def remove_from_querystring(url: str, params: List[str]):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query = without_keys(query, *params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def extract_from_querystring(url: str, params: List[str]):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    return with_keys(query, *params)


def sort_querystring(url: str):
    # Sorts querystring by key in ascending order. Useful for normalization
    # when comparing two urls for equivalence
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query = OrderedDict(sorted(query.items()))
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def dict_get(obj, *args, default=None):
    return tuple(obj.get(k, default) for k in args)


@contextmanager
def logger_temp_level(logger, new_level):
    old_level = logger.level
    try:
        logger.setLevel(new_level)
        yield
    finally:
        logger.setLevel(old_level)
