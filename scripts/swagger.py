import json 
import os 
import ast 
import subprocess
import pkg_resources

import toml

RAW_SPEC_PATH = './swagger_specs/swagger.json'
FORMATTED_SPEC_PATH = './swagger_specs/swagger_processed.json'
SWAGGER_CLIENT_PATH = './client'
SWAGGER_CLIENT_NAME = 'coingecko'
SWAGGER_API_CLIENT_PATH = os.path.join("./client/swagger_client/api/", f"{SWAGGER_CLIENT_NAME}_api.py")
URL_TO_METHOD_PATH = "./data/url_to_method.json"
POETRY_PROJECT_FILE_PATH = './pyproject.toml'
SWAGGER_REQUIREMENTS_PATH = os.path.join(SWAGGER_CLIENT_PATH, 'requirements.txt')
SWAGGER_REQUIREMENTS_DEV_PATH = os.path.join(SWAGGER_CLIENT_PATH, 'test-requirements.txt')

def generate_client(): 
    # pull the swagger spec from the coingecko website, write to local file 
    subprocess.call(
        f"curl https://www.coingecko.com/api/documentations/v3/swagger.json --output {RAW_SPEC_PATH}".split(" ")
    )

    # minimally process raw swagger spec. 
    with open (RAW_SPEC_PATH, 'r') as f: 
        spec = json.loads(f.read())
        for path, path_spec in spec['paths'].items(): 
            assert len(path_spec.keys()) == 1
            assert "get" in path_spec
            spec['paths'][path]['get']['tags'] = ['SWAGGER_CLIENT_NAME']
    with open(FORMATTED_SPEC_PATH, 'w') as f: 
        f.write(json.dumps(spec, indent=4))

    # auto-generate a base api client 
    subprocess.call(
        # command will overwrite contents of directory 
        f"swagger-codegen generate -i {FORMATTED_SPEC_PATH} -l python -o {SWAGGER_CLIENT_PATH}".split(" ")
    )

    # get a mapping from url templates to auto-generated methods 
    methods = []
    with open(SWAGGER_API_CLIENT_PATH, 'r') as f: 
        source = f.read()
    p = ast.parse(source)
    methods = [node.name for node in ast.walk(p) if isinstance(node, ast.FunctionDef)]
    url_to_method = dict()
    for url_template in spec['paths'].keys(): 
        parts = [p.replace("{", '').replace("}", "") for p in url_template.split("/") if p]
        method_name = "_".join(parts + ['get'])
        assert method_name in methods
        url_to_method[url_template] = method_name
    with open(URL_TO_METHOD_PATH, 'w') as f:
        f.write(json.dumps(url_to_method, indent=4))  

    # validate that all requirements of generated client are met by the poetry project file 
    with open(POETRY_PROJECT_FILE_PATH, 'r') as f: 
        poetry = toml.loads(f.read())
        deps = poetry['tool']['poetry']['dependencies']
    with open(SWAGGER_REQUIREMENTS_PATH, 'r') as f: 
        reqs = list(pkg_resources.parse_requirements(f))
    for r in reqs: 
        package = r.project_name.replace("-", "_")
        assert len(r.specs) == 1
        op, spec = r.specs[0] 
        assert op == ">="
        assert package in deps 
        assert f"^{spec}" == deps[package]


def generate_test_data(): 
    with open(URL_TO_METHOD_PATH, 'r') as f: 
        url_to_method = json.loads(f.read())
    
