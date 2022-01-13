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

from client.swagger_client import ApiClient as ApiClientSwagger 
from client.swagger_client.api import CoingeckoApi as CoinGeckoApiSwagger

from pycoingecko_extra.utils import without_keys, dict_get
from scripts.utils import get_url_base, materialize_url_template
from scripts.swagger import get_parameters

# This sets the root logger to write to stdout (your console).
logging.basicConfig()
logger = logging.getLogger("CoinGeckoAPIExtra")
logger.setLevel(10)

RATE_LIMIT_STATUS_CODE = 429

error_msgs = dict(
    exp_limit_reached="Waited for maximum specified time but was still rate limited. Try increasing exp_limit. Queued calls are retained."
)

class CoinGeckoAPIClient(ApiClientSwagger):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_timeout = 120
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries)) 
        self._include_resp = False 

    def call_api(
        self, 
        resource_path, 
        method,
        path_params,
        query_params,
        header_params,
        **kwargs 
    ):
        # TODO: all mandatory args (whether in path or query) must be included in args call to api 
        # need to update my data files with this information. 
        args = list(path_params.values()) # dictionaries are ordered from python 3.6 on so this is fine. 
        kwargs = {v[0]: v[1] for v in query_params} 
        url = materialize_url_template(resource_path, args, kwargs)
        logger.debug(f"HTTPS Request: {url}")
        # logger.debug(f"args: {args} kwargs: {kwargs}")
        assert method == "GET"
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


class CoinGeckoAPI(CoinGeckoApiSwagger):

    def __init__(self, *args):
        super().__init__(api_client=CoinGeckoAPIClient())