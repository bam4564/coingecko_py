import subprocess


def run_tests():
    subprocess.run(["ls", "."])
    subprocess.run("poetry run pytest ./tests".split(" "))
    # subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
