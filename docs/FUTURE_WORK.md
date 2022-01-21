- Downgrade python version to 3.5 
- Add section to docs about exceptions raised by api client 
  - If request is unsuccessful, raw response object is always available 
- Fix client liveness check. Currently the CICD pipeline is not running
  on schedule as intended. 
- Add pre-commit hook to 
  - run black code formatting 
- Add authentication for pro api endpoint. 