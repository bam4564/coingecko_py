import re
import os
import tempfile
import logging

import coingecko_py
from coingecko_py.utils.api_meta import api_meta
from coingecko_py.utils.constants import (
    FORMATTED_SPEC_PATH,
    COVERAGE_PATH,
)
from coingecko_py.scripts.swagger import (
    process_spec,
    download_spec,
    are_specs_equal,
)
from coingecko_py.utils.utils import logger_temp_level


def _get_cov_percent():
    with open(COVERAGE_PATH, "r") as f:
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
    """Prints the code coverage percentage"""
    print(_get_cov_percent())


def get_cov_color():
    """Prints the color to be used for code coverage badge"""
    percent = _get_cov_percent()
    if percent >= 80:
        color = "green"
    elif percent >= 50:
        color = "orange"
    else:
        color = "red"
    print(color)


def get_api_version():
    """Prints the Coingecko API version of the generated client code"""
    print(api_meta.get_api_version())


@logger_temp_level(logging.getLogger(coingecko_py.__name__), 0)
def github_specs_equal():
    """Prints boolean indicating whether or not OpenAPI spec used to generate client
    matches the OpenAPI spec downloaded from the coingecko website.

    It's necessary to disable the package logger here as this function's only output
    to stdout should be "True" or "False".
    """
    if not os.path.exists(FORMATTED_SPEC_PATH):
        raise ValueError(
            "When running this function, a downloaded client spec should always exist"
        )
    old_spec = api_meta.get_spec_processed()
    with tempfile.NamedTemporaryFile() as fp:
        file_path = fp.name
        new_spec = process_spec(download_spec(output_path=file_path, silent=True))
    print(are_specs_equal(old_spec, new_spec))
