General   
- Add ability to include the response in the data returned from the api. 
- Make it so that it is not required for page range queries to be queued. 
- Fix client liveness check. Currently the CICD pipeline is not running. 
  on schedule as intended. 
- Add pre-commit hook to 
  - run black code formatting 
- Dockerize the client code generation process 
- Async support for higher tiers 
