import subprocess


def run_tests():
    subprocess.run("pytest ./tests/test_swagger.py".split(" "))
    # subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
