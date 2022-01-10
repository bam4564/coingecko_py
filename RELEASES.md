# Releases 

This document outlines the process to follow when releasing new package versions. 

## Update Project Files 

1. Update the version of the project in `pyproject.toml`.  
2. Update the changelog for the new version.  

## Publish (PyPI)

```shell 
poetry publish --build` 
```

## Release (Github)

Create a github release using the new version. Include the zipped source and wheel created by poetry. 
