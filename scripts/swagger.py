import json
import os
import ast
import re
import subprocess
import pkg_resources
import urllib.parse as urlparse
from urllib.parse import urlencode

import urllib3
import toml

from scripts.utils import materialize_url_template

RAW_SPEC_PATH = "./swagger_specs/swagger.json"
FORMATTED_SPEC_PATH = "./swagger_specs/swagger_processed.json"
SWAGGER_CLIENT_PATH = "./client"
SWAGGER_CLIENT_NAME = "coingecko"
SWAGGER_API_CLIENT_PATH = os.path.join(
    "./client/swagger_client/api/", f"{SWAGGER_CLIENT_NAME}_api.py"
)
URL_TO_METHOD_PATH = "./data/url_to_method.json"
POETRY_PROJECT_FILE_PATH = "./pyproject.toml"
TEST_API_DATA_PATH = "data/test_api_calls.json"
TEST_API_RESPONSES_PATH = "data/test_api_responses.json"
SWAGGER_REQUIREMENTS_PATH = os.path.join(SWAGGER_CLIENT_PATH, "requirements.txt")
SWAGGER_REQUIREMENTS_DEV_PATH = os.path.join(
    SWAGGER_CLIENT_PATH, "test-requirements.txt"
)


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
    for p in ['/finance_platforms', '/finance_products']: 
        for i, param in enumerate(spec["paths"][p]['get']['parameters']): 
            if param['name'] in ['page', 'start_at', 'end_at']: 
                print("Performing spec fix for:", p)
                spec["paths"][p]['get']['parameters'][i]["in"] = "query"
    with open(FORMATTED_SPEC_PATH, "w") as f:
        f.write(json.dumps(spec, indent=4))

    # auto-generate a base api client
    subprocess.call(
        # command will overwrite contents of directory
        f"swagger-codegen generate -i {FORMATTED_SPEC_PATH} -l python -o {SWAGGER_CLIENT_PATH}".split(
            " "
        )
    )

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
    # with open(POETRY_PROJECT_FILE_PATH, "r") as f:
    #     poetry = toml.loads(f.read())
    #     deps = poetry["tool"]["poetry"]["dependencies"]
    # with open(SWAGGER_REQUIREMENTS_PATH, "r") as f:
    #     reqs = list(pkg_resources.parse_requirements(f))
    # for r in reqs:
    #     package = r.project_name.replace("-", "_")
    #     assert len(r.specs) == 1
    #     op, spec = r.specs[0]
    #     assert op == ">="
    #     assert package in deps
    #     assert f"^{spec}" == deps[package]


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
            materialize_url_template(url_template, data['args'], data["kwargs"])
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
    return spec['paths'][url_template]['get'].get('parameters', [])


def get_api_method_names(): 
    with open(URL_TO_METHOD_PATH, "r") as f:
        url_to_methods = json.loads(f.read())
    return list(url_to_methods.values())
