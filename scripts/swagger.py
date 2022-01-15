import json
import os
import ast
import re
import shutil
import subprocess
import pkg_resources
import urllib.parse as urlparse
from urllib.parse import urlencode
from collections import OrderedDict

import urllib3
import toml
from dotenv import load_dotenv

load_dotenv()


RAW_SPEC_PATH = os.environ["RAW_SPEC_PATH"]
FORMATTED_SPEC_PATH = os.environ["FORMATTED_SPEC_PATH"]
SWAGGER_CLIENT_PATH = os.environ["SWAGGER_CLIENT_PATH"]
SWAGGER_CLIENT_NAME = os.environ["SWAGGER_CLIENT_NAME"]
SWAGGER_API_CLIENT_PATH = os.environ["SWAGGER_API_CLIENT_PATH"]
SWAGGER_DATA_PATH = os.environ["SWAGGER_DATA_PATH"]
URL_TO_METHOD_PATH = os.environ["URL_TO_METHOD_PATH"]
POETRY_PROJECT_FILE_PATH = os.environ["POETRY_PROJECT_FILE_PATH"]
TEST_API_DATA_PATH = os.environ["TEST_API_DATA_PATH"]
TEST_API_RESPONSES_PATH = os.environ["TEST_API_RESPONSES_PATH"]
SWAGGER_REQUIREMENTS_PATH = os.environ["SWAGGER_REQUIREMENTS_PATH"]
SWAGGER_API_DOCS_PATH = os.environ["SWAGGER_API_DOCS_PATH"]
PROJECT_API_DOCS_PATH = os.environ["PROJECT_API_DOCS_PATH"]


def generate_client():
    # pull the swagger spec from the coingecko website, write to local file
    subprocess.call(
        f"curl https://www.coingecko.com/api/documentations/v3/swagger.json --output {RAW_SPEC_PATH}".split(
            " "
        )
    )

    # minimally process raw swagger spec.
    with open(RAW_SPEC_PATH, "r") as f:
        spec = json.loads(f.read())
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
    with open(FORMATTED_SPEC_PATH, "w") as f:
        f.write(json.dumps(spec, indent=4))

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
    with open(SWAGGER_API_CLIENT_PATH, "r") as f:
        source = f.read()
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
    with open(URL_TO_METHOD_PATH, "w") as f:
        f.write(json.dumps(url_to_method, indent=4))

    # validate that all requirements of generated client are met by the poetry project file
    with open(POETRY_PROJECT_FILE_PATH, "r") as f:
        poetry = toml.loads(f.read())
        deps = poetry["tool"]["poetry"]["dependencies"]
    with open(SWAGGER_REQUIREMENTS_PATH, "r") as f:
        reqs = list(pkg_resources.parse_requirements(f))
    # had to manually update package versions specified in requirements.txt
    # as they were incompatible with poetry dependencies
    req_overrides = dict(
        requests="^2.27.1",
        certifi="^2017.4.17",
        urllib3="^1.26.8",
    )
    for r in reqs:
        package = r.project_name.replace("-", "_")
        assert len(r.specs) == 1
        op, spec = r.specs[0]
        if package in req_overrides:
            # ensure this other package version already exists in poetry
            assert req_overrides[package] == deps[package]
        else:
            # ensure version in requirements.txt exactly matches poetry dep
            assert op == ">="
            assert package in deps
            assert f"^{spec}" == deps[package]

    # process the generated README and create a new one
    print(f"Generating: {PROJECT_API_DOCS_PATH}")
    with open(SWAGGER_API_DOCS_PATH, "r") as f:
        text = f.read()
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
    # update hyperlinks within the document
    print(os.path.basename(SWAGGER_API_DOCS_PATH))
    text = text.replace("CoingeckoApi.md", os.path.basename(PROJECT_API_DOCS_PATH))
    with open(PROJECT_API_DOCS_PATH, "w") as f:
        f.write(text)

    # auto-format generated code
    subprocess.call(f"poetry run black .".split(" "))


def generate_test_data_template():
    template = dict()
    with open(FORMATTED_SPEC_PATH, "r") as f:
        spec = json.loads(f.read())
    for path, path_spec in spec["paths"].items():
        template[path] = {"args": list(), "kwargs": dict()}
        assert "get" in path_spec
        params = path_spec["get"].get("parameters", list())
        for p in params:
            assert p["in"] in ["path", "query"]
            if p["in"] == "query":
                template[path]["kwargs"][p["name"]] = p["type"]
    with open(TEST_API_DATA_PATH, "w") as f:
        f.write(json.dumps(template, indent=4))


def generate_test_data():
    with open(TEST_API_DATA_PATH, "r") as f:
        test_api_calls = json.loads(f.read())
    # Generate urls to request from the test api call spec
    urls = [
        (
            url_template,
            materialize_url_template(url_template, data["args"], data["kwargs"]),
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
    with open(TEST_API_RESPONSES_PATH, "w") as f:
        f.write(json.dumps(data, indent=4))


def get_parameters(url_template):
    with open(FORMATTED_SPEC_PATH, "r") as f:
        spec = json.loads(f.read())
    return spec["paths"][url_template]["get"].get("parameters", [])


def get_url_to_methods():
    with open(URL_TO_METHOD_PATH, "r") as f:
        url_to_methods = json.loads(f.read())
    return url_to_methods


def get_expected_response():
    with open("swagger_data/test_api_responses.json", "r") as f:
        expected_response = json.loads(f.read())
    return expected_response


def get_test_api_calls():
    with open("swagger_data/test_api_calls.json", "r") as f:
        test_api_calls = json.loads(f.read())
    return test_api_calls


def get_api_method_names():
    url_to_methods = get_url_to_methods()
    return list(url_to_methods.values())


def get_paginated_method_names():
    url_to_methods = get_url_to_methods()
    paged_method_names = list()
    for url_template, method_name in url_to_methods.items():
        params = filter(
            lambda p: p["name"] in ["page", "per_page"], get_parameters(url_template)
        )
        if len(list(params)) == 2:
            paged_method_names.append(method_name)
    return paged_method_names


def materialize_url_template(url_template, args, kwargs):
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
    url_base = get_url_base()
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


def get_url_base():
    with open(FORMATTED_SPEC_PATH, "r") as f:
        spec = json.loads(f.read())
    host = spec["host"]
    basePath = spec["basePath"]
    schemes = spec["schemes"]
    assert len(schemes) == 1
    scheme = schemes[0]
    url_parts = [scheme, host, basePath, "", "", ""]
    url = urlparse.urlunparse(url_parts)
    return url
