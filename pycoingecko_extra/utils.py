from typing import List
import urllib.parse as urlparse
from urllib.parse import urlencode, urlunparse


def update_querystring(url: str, params: dict):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def remove_from_querystring(url: str, params: List[str]):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    for k in params:
        if k in query:
            del query[k]
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def extract_from_querystring(url: str, params: List[str]):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    return {k: v for k, v in query.items() if k in params}
