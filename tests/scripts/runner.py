import subprocess


def run_tests():
    subprocess.run("pwd && ls && pytest ./tests".split(" "))
    # subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
