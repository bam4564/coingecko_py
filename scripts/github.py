import re


def _get_cov_percent():
    with open("cov.xml", "r") as f:
        lines = f.readlines()
    match = float(re.findall(r'line-rate="([^"]*)"', lines[1])[0])
    percent = round(match * 100, 2)
    return percent


def get_cov_percent():
    print(_get_cov_percent())


def get_cov_color():
    percent = _get_cov_percent()
    if percent >= 80:
        return "green"
    elif percent >= 50:
        return "orange"
    else:
        return "red"
