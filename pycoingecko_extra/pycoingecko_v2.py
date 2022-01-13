import time
import math
import logging
import requests
import itertools
import json
import requests 
from typing import List, Set
from collections import defaultdict, deque
from functools import partial
from contextlib import contextmanager
from pycoingecko import CoinGeckoAPI
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from client.swagger_client import ApiClient

from pycoingecko_extra.utils import without_keys, dict_get
from scripts.utils import get_url_base, materialize_url_template

# This sets the root logger to write to stdout (your console).
logging.basicConfig()
logger = logging.getLogger("CoinGeckoAPIExtra")
logger.setLevel(10)

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing exp_limit. Queued calls are retained."
)

class CoinGeckoAPIClient(ApiClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_base_url = get_url_base()
        self.request_timeout = 120
        self.session = requests.Session()
        self._include_resp = False 
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries)) 

    def call_api(
        self, 
        resource_path, 
        method,
        path_params=None, 
        query_params=None, 
        header_params=None,
        body=None, 
        **kwargs 
    ):
        url = materialize_url_template(
            resource_path, 
            [v for v in path_params.items()], # dictionaries are ordered from python 3.6 on so this is fine. 
            {v[0]: v[1] for v in query_params} 
        )
        print(url)
        assert method == "GET"
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
