import json
import os
import ast
import re
import shutil
import subprocess
import urllib.parse as urlparse
from urllib.parse import urlencode

import urllib3
from deepdiff import DeepDiff
from dotenv import load_dotenv

load_dotenv()


RAW_SPEC_PATH = os.environ["RAW_SPEC_PATH"]
FORMATTED_SPEC_PATH = os.environ["FORMATTED_SPEC_PATH"]
DIFF_SPEC_PATH = os.environ["DIFF_SPEC_PATH"]
SWAGGER_CLIENT_PATH = os.environ["SWAGGER_CLIENT_PATH"]
SWAGGER_CLIENT_NAME = os.environ["SWAGGER_CLIENT_NAME"]
SWAGGER_API_CLIENT_PATH = os.environ["SWAGGER_API_CLIENT_PATH"]
SWAGGER_DATA_PATH = os.environ["SWAGGER_DATA_PATH"]
URL_TO_METHOD_PATH = os.environ["URL_TO_METHOD_PATH"]
TEST_API_CALLS_PATH = os.environ["TEST_API_CALLS_PATH"]
TEST_API_RESPONSES_PATH = os.environ["TEST_API_RESPONSES_PATH"]
SWAGGER_API_DOCS_PATH = os.environ["SWAGGER_API_DOCS_PATH"]
PROCESSED_DOCS_PATH = os.environ["PROCESSED_DOCS_PATH"]
SPEC_CHECK = False


class ApiData:

    """GENERIC I/O"""

    def read(self, path, is_json=True):
        with open(path, "r") as f:
            data = f.read()
            if is_json:
                data = json.loads(data)
        return data

    def write(self, path, data, is_json=True):
        with open(path, "w") as f:
            if is_json:
                data = json.dumps(data, indent=4)
            f.write(data)

    """ READS """

    def get_spec_raw(self):
        return self.read(RAW_SPEC_PATH)

    def get_spec_processed(self):
        return self.read(FORMATTED_SPEC_PATH)

    def get_docs_generated(self):
        return self.read(SWAGGER_API_DOCS_PATH, is_json=False)

    def get_api_client_source_code(self):
        return self.read(SWAGGER_API_CLIENT_PATH, is_json=False)

    def get_test_api_calls(self):
        return self.read(TEST_API_CALLS_PATH)

    def get_url_to_method(self):
        return self.read(URL_TO_METHOD_PATH)

    def get_test_api_responses(self):
        return self.read(TEST_API_RESPONSES_PATH)

    def get_parameters(self, url_template):
        spec = self.get_spec_processed()
        return spec["paths"][url_template]["get"].get("parameters", [])

    def get_url_base(self):
        spec = self.get_spec_processed()
        host = spec["host"]
        basePath = spec["basePath"]
        schemes = spec["schemes"]
        assert len(schemes) == 1
        scheme = schemes[0]
        url_parts = [scheme, host, basePath, "", "", ""]
        url = urlparse.urlunparse(url_parts)
        return url

    def get_api_method_names(self):
        return list(self.get_url_to_method().values())

    def get_paginated_method_names(self):
        url_to_methods = self.get_url_to_method()
        paged_method_names = list()
        for url_template, method_name in url_to_methods.items():
            params = filter(
                lambda p: p["name"] in ["page", "per_page"],
                self.get_parameters(url_template),
            )
            if len(list(params)) == 2:
                paged_method_names.append(method_name)
        return paged_method_names

    """ WRITES """

    def write_spec_processed(self, spec):
        self.write(FORMATTED_SPEC_PATH, spec)

    def write_spec_diff(self, diff):
        self.write(DIFF_SPEC_PATH, diff, is_json=False)

    def write_docs_processed(self, text):
        self.write(PROCESSED_DOCS_PATH, text, is_json=False)

    def write_url_to_method(self, url_to_method):
        self.write(URL_TO_METHOD_PATH, url_to_method)

    def write_test_api_calls(self, test_api_calls):
        self.write(TEST_API_CALLS_PATH, test_api_calls)

    def write_test_api_responses(self, test_api_responses):
        self.write(TEST_API_RESPONSES_PATH, test_api_responses)

    """ OTHER """

    def materialize_url_template(self, url_template, args, kwargs):
        """Converts url template to url to request from api by adding prefix and encoding args, kwargs

        input:
            url_template = "/coins/{id}/contract/{contract_address}/market_chart/range"
            args = ["ethereum", "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"]
            kwargs = {
                "vs_currency": "eur",
                "from": "1622520000",
                "to": "1638334800"
            }

        output:
            https://api.coingecko.com/api/v3/coins/ethereum/contract/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984/market_chart/range?vs_currency=eur&from=1622520000&to=1638334800
        """
        url_base = api_data.get_url_base()
        url_base_parts = list(urlparse.urlparse(url_base))
        # transform /coins/{id}/contract/{contract_address} ---> /coins/{0}/contract/{1}
        path_args = re.findall(r"({[^}]*})", url_template)
        url = url_template
        for i, p in enumerate(path_args):
            url = url.replace(p, "{" + str(i) + "}")
        # construct full url
        url_parts = list(urlparse.urlparse(url))
        url_parts[0] = url_base_parts[0]
        url_parts[1] = url_base_parts[1]
        # add args to path
        url_parts[2] = url_base_parts[2] + url.format(*args)
        # add kwargs as query string parameters
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(kwargs)
        url_parts[4] = urlencode(query)
        url = urlparse.urlunparse(url_parts)
        return url


api_data = ApiData()


def generate_client():
    # pull the swagger spec from the coingecko website, write to local file
    subprocess.call(
        f"curl https://www.coingecko.com/api/documentations/v3/swagger.json --output {RAW_SPEC_PATH}".split(
            " "
        )
    )

    # minimally process raw swagger spec.
    spec = api_data.get_spec_raw()
    for path, path_spec in spec["paths"].items():
        assert len(path_spec.keys()) == 1
        assert "get" in path_spec
        spec["paths"][path]["get"]["tags"] = [SWAGGER_CLIENT_NAME]
    # TODO: The coingecko API spec has some errors. This fixes them. Will remove once they update their spec
    for p in ["/finance_platforms", "/finance_products"]:
        for i, param in enumerate(spec["paths"][p]["get"]["parameters"]):
            if param["name"] in ["page", "start_at", "end_at"]:
                print("Performing spec fix for:", p)
                spec["paths"][p]["get"]["parameters"][i]["in"] = "query"

    # for diff testing
    # spec["new_key"] = 6

    # check to see if the generated spec is different from the downloaded  + processed spec
    if SPEC_CHECK and os.path.exists(FORMATTED_SPEC_PATH):
        spec_existing = api_data.get_spec_processed()
        diff = DeepDiff(spec_existing, spec)
        if not diff:
            print(f"Old spec matches new spec. Exiting.")
            api_data.write_spec_diff("")
            return
        if diff:
            print(f"Downloaded spec different from existing spec.")
            api_data.write_spec_diff(diff.pretty())
    else:
        api_data.write_spec_processed(spec)

    # Remove previously generated client
    if os.path.isdir(SWAGGER_CLIENT_PATH):
        shutil.rmtree(SWAGGER_CLIENT_PATH)
    os.mkdir(SWAGGER_CLIENT_PATH)
    # auto-generate a base api client
    subprocess.call(
        # command will overwrite contents of directory
        f"swagger-codegen generate -i {FORMATTED_SPEC_PATH} -l python -o {SWAGGER_CLIENT_PATH}".split(
            " "
        )
    )

    # generate directory for swagger data if it does not already exist
    if not os.path.isdir(SWAGGER_DATA_PATH):
        os.mkdir(SWAGGER_DATA_PATH)

    # get a mapping from url templates to auto-generated methods
    methods = []
    source = api_data.get_api_client_source_code()
    p = ast.parse(source)
    methods = [node.name for node in ast.walk(p) if isinstance(node, ast.FunctionDef)]
    url_to_method = dict()
    for url_template in spec["paths"].keys():
        parts = [
            p.replace("{", "").replace("}", "") for p in url_template.split("/") if p
        ]
        method_name = "_".join(parts + ["get"])
        assert method_name in methods
        url_to_method[url_template] = method_name
    api_data.write_url_to_method(url_to_method)

    # process the generated README and create a new one
    print(f"Generating: {PROCESSED_DOCS_PATH}")
    text = api_data.get_docs_generated()
    # process example code blocks to remove unnecessary stuff, update stuff that's different
    import_old = "\n".join(
        [
            "from __future__ import print_function",
            "import time",
            "import swagger_client",
            "from swagger_client.rest import ApiException",
            "from pprint import pprint",
        ]
    )
    import_new = "from py_coingecko import CoingeckoApi"
    text = text.replace(import_old, import_new)
    matches = re.findall(
        r"(try:\n.*?(api_instance\.[^\)]*?\)).*?)\n```",
        text,
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    for m in matches:
        text = text.replace(m[0], f"res = {m[1]}")
    text = text.replace("swagger_client.", "")
    text = text.replace("api_instance", "cg")
    text = text.replace("<b>", "").replace("</b>", "")
    text = text.replace("&lt;b&gt;", "**").replace("&lt;/b&gt;", "**")

    # update hyperlinks within the document
    print(os.path.basename(SWAGGER_API_DOCS_PATH))
    text = text.replace("CoingeckoApi.md", os.path.basename(PROCESSED_DOCS_PATH))
    api_data.write_docs_processed(text)

    # auto-format generated code
    subprocess.call(f"poetry run black .".split(" "))


def generate_test_data_template():
    template = dict()
    spec = api_data.get_spec(processed=True)
    for path, path_spec in spec["paths"].items():
        template[path] = {"args": list(), "kwargs": dict()}
        assert "get" in path_spec
        params = path_spec["get"].get("parameters", list())
        for p in params:
            assert p["in"] in ["path", "query"]
            if p["in"] == "query":
                template[path]["kwargs"][p["name"]] = p["type"]
    api_data.write_test_api_calls(template)


def generate_test_data():
    test_api_calls = api_data.get_test_api_calls()
    # Generate urls to request from the test api call spec
    urls = [
        (
            url_template,
            api_data.materialize_url_template(
                url_template, data["args"], data["kwargs"]
            ),
        )
        for url_template, data in test_api_calls.items()
    ]
    # perform api calls to get test data for mock based testing.
    pool_manager = urllib3.PoolManager(num_pools=4, maxsize=4)
    data = dict()
    for url_template, url in urls:
        print(url)
        r = pool_manager.request("GET", url)
        if r.status != 200:
            raise Exception(r.status)
        content = json.loads(r.data.decode("utf-8"))
        assert content
        data[url_template] = content
    # write responses to file
    api_data.write_test_api_responses(data)
