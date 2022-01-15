import subprocess


def run_tests():
    subprocess.run("poetry run pytest ./tests -vvv".split(" "))
