import json
import os
import ast
import re
import shutil
import subprocess
import pkg_resources

import urllib3
from deepdiff import DeepDiff
from dotenv import load_dotenv

from ..py_coingecko.api_meta import api_meta

load_dotenv()


POETRY_PROJECT_FILE_PATH = os.environ["POETRY_PROJECT_FILE_PATH"]
RAW_SPEC_PATH = os.environ["RAW_SPEC_PATH"]
FORMATTED_SPEC_PATH = os.environ["FORMATTED_SPEC_PATH"]
DIFF_SPEC_PATH = os.environ["DIFF_SPEC_PATH"]
SWAGGER_CLIENT_PATH = os.environ["SWAGGER_CLIENT_PATH"]
SWAGGER_CLIENT_NAME = os.environ["SWAGGER_CLIENT_NAME"]
SWAGGER_API_CLIENT_PATH = os.environ["SWAGGER_API_CLIENT_PATH"]
SWAGGER_REQUIREMENTS_PATH = os.environ["SWAGGER_REQUIREMENTS_PATH"]
SWAGGER_DATA_PATH = os.environ["SWAGGER_DATA_PATH"]
URL_TO_METHOD_PATH = os.environ["URL_TO_METHOD_PATH"]
TEST_API_CALLS_PATH = os.environ["TEST_API_CALLS_PATH"]
TEST_API_RESPONSES_PATH = os.environ["TEST_API_RESPONSES_PATH"]
SWAGGER_API_DOCS_PATH = os.environ["SWAGGER_API_DOCS_PATH"]
PROCESSED_DOCS_PATH = os.environ["PROCESSED_DOCS_PATH"]
SPEC_CHECK = False


def generate_client():
    # pull the swagger spec from the coingecko website, write to local file
    subprocess.call(
        f"curl https://www.coingecko.com/api/documentations/v3/swagger.json --output {RAW_SPEC_PATH}".split(
            " "
        )
    )

    # minimally process raw swagger spec.
    spec = api_meta.get_spec_raw()
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
        spec_existing = api_meta.get_spec_processed()
        diff = DeepDiff(spec_existing, spec)
        if not diff:
            print(f"Old spec matches new spec. Exiting.")
            api_meta.write_spec_diff("")
            return
        if diff:
            print(f"Downloaded spec different from existing spec.")
            api_meta.write_spec_diff(diff.pretty())
    else:
        api_meta.write_spec_processed(spec)

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

    # validate that all requirements of generated client are met by the poetry project file
    deps = api_meta.get_poetry_dependencies()
    reqs = api_meta.get_swagger_requirements()
    # had to manually update package versions specified in requirements.txt
    # as they were incompatible with poetry dependencies
    req_overrides = ["requests", "certifi", "urllib3"]
    req_skips = ["setuptools"]
    for r in reqs:
        package = r.project_name.replace("-", "_")
        assert len(r.specs) == 1
        op, ver = r.specs[0]
        if package in req_skips:
            continue
        elif package in req_overrides:
            assert package in deps
        else:
            # ensure version in requirements.txt exactly matches poetry dep
            assert op == ">="
            assert package in deps
            assert f"^{ver}" == deps[package]

    # generate directory for swagger data if it does not already exist
    if not os.path.isdir(SWAGGER_DATA_PATH):
        os.mkdir(SWAGGER_DATA_PATH)

    # get a mapping from url templates to auto-generated methods
    methods = []
    source = api_meta.get_api_client_source_code()
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
    api_meta.write_url_to_method(url_to_method)

    # process the generated README and create a new one
    print(f"Generating: {PROCESSED_DOCS_PATH}")
    text = api_meta.get_docs_generated()
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
    text = text.replace("CoingeckoApi.md", os.path.basename(PROCESSED_DOCS_PATH))
    print(os.path.basename(SWAGGER_API_DOCS_PATH))
    api_meta.write_docs_processed(text)

    # cleanup the directory containing the generated code
    generated_delete = [
        ".swagger-codegen",
        "docs",
        "swagger_client.egg-info",
        "test",
        ".gitignore",
        ".swagger-codegen-ignore",
        ".travis.yml",
        "git_push.sh",
        "README.md",
        "requirements.txt",
        "test-requirements.txt",
        "tox.ini",
        # "setup.py",
    ]
    for name in generated_delete:
        path = os.path.join(SWAGGER_CLIENT_PATH, name)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    # auto-format generated code
    subprocess.call(f"poetry run black .".split(" "))


def generate_test_data_template():
    template = dict()
    spec = api_meta.get_spec(processed=True)
    for path, path_spec in spec["paths"].items():
        template[path] = {"path": list(), "query": dict()}
        assert "get" in path_spec
        params = path_spec["get"].get("parameters", list())
        for p in params:
            _in = p["in"]
            assert _in in ["path", "query"]
            if _in == "query":
                template[path][_in][p["name"]] = p["type"]
            else:
                template[path][_in].append(p["type"])
    api_meta.write_test_api_calls(template)


def generate_test_data():
    test_api_calls = api_meta.get_test_api_calls()
    # Generate urls to request from the test api call spec
    urls = [
        (
            url_template,
            api_meta.materialize_url_template(
                url_template, data["path"], data["query"]
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
    api_meta.write_test_api_responses(data)
