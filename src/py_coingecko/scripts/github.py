import re
import os
import tempfile
import logging

from src.py_coingecko.utils.api_meta import api_meta
from src.py_coingecko.utils.constants import (
    FORMATTED_SPEC_PATH,
)
from src.py_coingecko.scripts.swagger import (
    process_spec,
    download_spec,
    are_specs_equal,
)
from src.py_coingecko.utils.utils import logger_temp_level

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(0)


def _get_cov_percent():
    # TODO: add a constant here
    with open("cov.xml", "r") as f:
        lines = f.readlines()
    match = float(re.findall(r'line-rate="([^"]*)"', lines[1])[0])
    percent = round(match * 100, 2)
    return percent


""" Since the scripts below are used as part of a github action to set 
    environment variables, they should print their results rather than 
    return them. The shell script will use stdout of these scripts when 
    setting up env vars. 
"""


def get_cov_percent():
    print(_get_cov_percent())


def get_cov_color():
    percent = _get_cov_percent()
    if percent >= 80:
        color = "green"
    elif percent >= 50:
        color = "orange"
    else:
        color = "red"
    print(color)


def get_api_version():
    print(api_meta.get_api_version())


def github_specs_equal():
    """Script leveraged by github actions to check if downloaded spec equals existing spec"""
    import src.py_coingecko as pycg

    logger = logging.getLogger(pycg.__name__)
    with logger_temp_level(logger, 0):
        if not os.path.exists(FORMATTED_SPEC_PATH):
            raise ValueError(
                "When running this function, a downloaded client spec should always exist"
            )
        old_spec = api_meta.get_spec_processed()
        with tempfile.NamedTemporaryFile() as fp:
            file_path = fp.name
            new_spec = process_spec(download_spec(output_path=file_path, silent=True))
        print(are_specs_equal(old_spec, new_spec))
