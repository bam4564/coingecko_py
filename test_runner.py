import os
import subprocess

"""
Downloads the test file for the pycoingecko api client. Updates this file so that 
1. The subclass is imported instead of the base class 
2. All references to the base class become references to the subclass 

This allows us to 
1. Ensure that the subclass works exactly as the base class (i.e. it is a drop in replacement)
2. Test the new functionality added to the api client 
"""


def run_tests():
    USE_CACHED = False  # For development purposes only
    TEST_FILE_PATH = "tests/test_api.py"
    if USE_CACHED:
        if not os.path.exists(TEST_FILE_PATH):
            raise Exception(
                f"USE_CACHED was True but there is no cached file. Re-run and set to False."
            )
        print(f"Using previously downloaded version of file: ${TEST_FILE_PATH}")
    else:
        subprocess.call(
            f"curl https://raw.githubusercontent.com/man-c/pycoingecko/master/tests/test_api.py --output {TEST_FILE_PATH}".split(
                " "
            )
        )
        if not os.path.exists(TEST_FILE_PATH):
            raise Exception(f"curl failed to download test file.")
        with open(TEST_FILE_PATH, "r") as f:
            text = f.read()
            assert "from pycoingecko" in text
            assert "CoinGeckoAPI" in text
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                text.replace(
                    "from pycoingecko", "from pycoingecko_extra.pycoingecko_extra"
                ).replace("CoinGeckoAPI", "CoinGeckoAPIExtra")
            )
    # TODO: Generate output coverage report and use this to create badge in readme
    # subprocess.run("pytest --cov tests ".split(" "))
    subprocess.run("pytest -p no:cacheprovider tests ".split(" "))
