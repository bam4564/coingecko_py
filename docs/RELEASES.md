# Releases 

This document outlines the process to follow when releasing new package versions. 

New features and fixes should be introduced to the master branch via a pull request 
from a feature branch. Thus, all commits to the master branch should be accompanied 
by a release (publishing to PyPI and creating a release tag on github with the built
source code). 

To start this process, ensure you are on a feature branch where you have made changes. 

## 1. Ensuring The Swagger Client is Up to Date 

Ensure that the `swagger-codegen` generated api client is up to date with the 
OpenAPI specifaction available [here](https://www.coingecko.com/api/documentations/v3/swagger.json) 
on the coingecko website.

To do this, run: 

```shell
poetry run generate_client 
```

This script will download the spec, perform some minimal processing on it, then compare it 
with the existing [local spec](../swagger_data/swagger_processed.json) which was produced 
on a previous run of this same script. 

- If the two specs are the same, the script will exit as everything is up to date. 
- If the two specs are different, the script will. 
  - Write a diff of the two specs to [`swagger_data/swagger_processed_diff.json`](../swagger_data/swagger_processed_diff.txt). 
  - Replace the old client implementation with a new client implementation in the 
  [`swagger_generated`](https://github.com/brycemorrow4564/pycoingecko-extra/tree/master/swagger_generated) directory. 
  - Generate a new metadata file containing a mapping of url templates from the swagger 
  specification to the auto-generated method names at [`swagger_data/url_to_method.json`](../swagger_data/url_to_method.json). 
  - Re-generate the API documentation at [`docs/API.md`](./API.md). 
    - Check the auto-generated docs to ensure they it looks okay, as it is a processed version of the original. 
  - Format source code with `black`. 

If the two specs were different, there are a few more manual steps to perform. 

- Check [`swagger_data/swagger_processed_diff`](../swagger_data/swagger_processed_diff.txt). 
  - This will explain what changed from the previous spec to the current spec. 
  - Use this information to update [swagger_data/test_api_calls.json](../swagger_data/test_api_calls.json). 
  This file contains a mapping from url templates to the set of path and query arguments for a test api call. 
  Test API calls are used to generate test data (real data from coingecko) and also within the test suite. 
    - Add / remove any endpoints that changed. 
    - Add / remove any path or query arguments that changed. 
- After updating the test api calls, run `poetry run generate_test_data` 
  - This will use the test API calls to construct urls and query the coingecko API. The responses
  are used as mock data within the test suite. These data objects are written to [swagger_data/test_api_responses.json](../swagger_data/test_api_responses.json). 
    - This should only succeed if you properly made edits to the new spec in the prior step. 
    - Manually inspect the data for validity after this command completes successfully. 

At this point, all of our generated code and documentation is correct. 

## Code Formatting 

Enforce code formatting quality by running

```shell
poetry run black . 
```

## Unit and Integration Testing 

Perform the unit and integration tests by running

```shell
poetry run test 
```

All tests should pass and you should ensure code coverage is at least 80%.

## Update Project Files 

1. Update the version of the project in `pyproject.toml`. This project uses [semver](https://semver.org/)
2. Update [docs/CHANGELOG.md](./CHANGELOG.md) for the new version.  

## Commit Changes 

After completing all prior steps, ensure all changes are pushed to your remote feature 
branch. 

## Validate CICD Pipeline Passes Checks 

After pushing your changes to github, check to see that the CICD pipeline succeeds.

The status of the testing and code coverage stages are visible via badges in the README. 

## Merge to Master 

Once the CICD pipeline is successful, make a pull request into the master branch. 

Review any code changes once more, then merge into master. 

## Publish (PyPI)

To build the source code and executables and publish them to PyPI, run the following

```shell 
poetry publish --build
```

## Release (Github)

Create a github release using the new version. Include the zipped source and wheel created 
by poetry in your local `dist` directory. This directory is not currently versioned. 
