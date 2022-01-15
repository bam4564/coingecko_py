import re


def get_cov_percent():
    with open("cov.xml", "r") as f:
        lines = f.readlines()
    match = float(re.findall(r'line-rate="([^"]*)"', lines[1])[0])
    percent = round(match * 100, 2)
    print(percent)
