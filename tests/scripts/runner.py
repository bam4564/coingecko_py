import subprocess


def run_tests():
    subprocess.run("pytest tests ".split(" "))
    # subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
