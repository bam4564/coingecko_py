Next PR 
- Downgrade python version to 3.5 
- Add support for authentication for pro endpoint 
- Add check to ensure that qid is a string to api wrapper function 
- Add authentication for pro api endpoint. 

General 
- Add section to docs about exceptions raised by api client 
  - If request is unsuccessful, raw response object is always available 
- Fix client liveness check. Currently the CICD pipeline is not running
  on schedule as intended. 
- Add pre-commit hook to 
  - run black code formatting 
