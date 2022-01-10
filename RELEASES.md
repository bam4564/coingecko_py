# Releases 

This document outlines the process to follow when releasing new package versions. 

First, ensure all local changes are committed. Also ensure that code quality is enforced: 
```shell
poetry run black 
```

## Update Project Files 

1. Update the version of the project in `pyproject.toml`.  
2. Update the changelog for the new version.  

## Publish (PyPI)

```shell 
poetry publish --build
```

## Release (Github)

Create a github release using the new version. Include the zipped source and wheel created by poetry. 
