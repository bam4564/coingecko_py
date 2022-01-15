import subprocess


def run_tests():
    subprocess.run("poetry run pytest ./tests --cov -vvv".split(" "))
    # subprocess.run("poetry run pytest ./tests --cov -vvv".split(" "))
