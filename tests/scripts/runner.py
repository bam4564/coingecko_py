import subprocess


def run_tests():
    subprocess.run(["ls", "."])
    subprocess.run(["echo", "'\n'"])
    subprocess.run(["ls", "./tests"])
    subprocess.run("poetry run pytest ./tests -vvv".split(" "))
    # subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
