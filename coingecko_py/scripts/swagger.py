import json
import os
import ast
import re
import shutil
import subprocess
import logging

import urllib3
from deepdiff import DeepDiff

from coingecko_py.utils.api_meta import api_meta
from coingecko_py.utils.utils import logger_temp_level
from coingecko_py.utils.constants import (
    RAW_SPEC_PATH,
    FORMATTED_SPEC_PATH,
    SWAGGER_CLIENT_PATH,
    SWAGGER_CLIENT_NAME,
    SWAGGER_DATA_PATH,
    SWAGGER_API_DOCS_PATH,
    PROCESSED_DOCS_PATH,
)


logging.basicConfig()
logger = logging.getLogger(__name__)


def download_spec(output_path=RAW_SPEC_PATH, silent=False):
    """Downloads coingecko API spec. Returns as dict. Will raise an exception if command fails."""
    input_path = "https://www.coingecko.com/api/documentations/v3/swagger.json"
    args = ["curl", input_path, "--output", output_path]
    if silent:
        args.append("-s")
    subprocess.run(args, check=True)
    spec = api_meta.get_spec_raw()
    return spec


def process_spec(spec):
    """Post-processes downloaded spec.
    - Changes all tags to have same value, so a single API client is generated
    - Fixes issues with spec (uncovered during testing)
    """
    for path, path_spec in spec["paths"].items():
        assert len(path_spec.keys()) == 1
        assert "get" in path_spec
        spec["paths"][path]["get"]["tags"] = [SWAGGER_CLIENT_NAME]
    # TODO: The coingecko API spec has some errors. This fixes them. Will remove once they update their spec
    for p in ["/finance_platforms", "/finance_products"]:
        for i, param in enumerate(spec["paths"][p]["get"]["parameters"]):
            if param["name"] in ["page", "start_at", "end_at"]:
                logger.info("Performing spec fix for: " + p)
                spec["paths"][p]["get"]["parameters"][i]["in"] = "query"
    return spec


def are_specs_equal(spec, spec_existing):
    """Performs a diff on existing and new specs (both post-processing)
    - Writes diff to file
    """
    diff = DeepDiff(spec_existing, spec)
    if not diff:
        logger.info(f"Old spec matches new spec.")
        api_meta.write_spec_diff("")
        return True
    if diff:
        logger.info(f"Downloaded spec different from existing spec.")
        api_meta.write_spec_diff(diff.pretty())
        return False


def generate_client_code():
    # Remove previously generated client
    if os.path.isdir(SWAGGER_CLIENT_PATH):
        shutil.rmtree(SWAGGER_CLIENT_PATH)
    os.mkdir(SWAGGER_CLIENT_PATH)
    # auto-generate a base api client
    args = [
        "swagger-codegen",
        "generate",
        "-i",
        FORMATTED_SPEC_PATH,
        "-l",
        "python",
        "-o",
        SWAGGER_CLIENT_PATH,
    ]
    subprocess.run(args, check=True)


def validate_dependencies():
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


def generate_url_to_method_map(spec):
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


def generate_readme():
    # process the generated README and create a new one
    logger.info(f"Generating: {PROCESSED_DOCS_PATH}")
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
    import_new = "from coingecko_py import CoingeckoApi"
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
    logger.info(os.path.basename(SWAGGER_API_DOCS_PATH))
    api_meta.write_docs_processed(text)


def generated_code_cleanup():
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


def generated_code_fix_imports():
    # fix imports within the generated code
    for dirpath, dirnames, filenames in os.walk(SWAGGER_CLIENT_PATH):
        for f in filenames:
            if f.endswith(".py"):
                path = os.path.join(dirpath, f)
                with open(path, "r") as file:
                    source = file.read()
                source = source.replace(
                    "from swagger_client",
                    "from coingecko_py.swagger_generated.swagger_client",
                )
                source = source.replace(
                    "import swagger_client",
                    "import coingecko_py.swagger_generated.swagger_client",
                )
                with open(path, "w") as file:
                    file.write(source)


@logger_temp_level(logger, logging.INFO)
def generate_client():
    SPEC_CHECK = True  # Should only be False when developing
    spec = process_spec(download_spec())
    if (
        SPEC_CHECK
        and os.path.exists(FORMATTED_SPEC_PATH)
        and are_specs_equal(spec, api_meta.get_spec_processed())
    ):
        return
    api_meta.write_spec_processed(spec)
    generate_client_code()
    validate_dependencies()
    # generate directory for swagger metadata
    if not os.path.isdir(SWAGGER_DATA_PATH):
        os.mkdir(SWAGGER_DATA_PATH)
    generate_url_to_method_map(spec)
    generate_readme()
    generated_code_cleanup()
    generated_code_fix_imports()
    subprocess.run(f"poetry run black .".split(" "), check=True)


@logger_temp_level(logger, logging.INFO)
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


@logger_temp_level(logger, logging.INFO)
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
        logger.info(url)
        r = pool_manager.request("GET", url)
        if r.status != 200:
            raise Exception(r.status)
        content = json.loads(r.data.decode("utf-8"))
        assert content
        data[url_template] = content
    # write responses to file
    api_meta.write_test_api_responses(data)
