import subprocess


def run_tests():
    subprocess.run("pytest ./tests --cov -vvv".split(" "))
    # -o log_cli=true
    # -k test_failed_body_byte_decode
    # subprocess.run("poetry run pytest ./tests --cov -vvv".split(" "))
    # subprocess.run("poetry run pytest ./tests --cov -vvv".split(" "))
