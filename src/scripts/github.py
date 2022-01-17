import re

from src.py_coingecko.api_meta import api_meta


def _get_cov_percent():
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
