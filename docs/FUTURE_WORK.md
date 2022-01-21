Current Branch
- Update client configuration section of docs explaining how to 
  set the api key on the client. 
- Downgrade python version to 3.5 (min version supported for poetry projects). 
- Add a badge specifying supported python versions to README. 
- Add section on exception handling to README
  - Rationale for why response is not exposed (only necessary for pagination
  and the client already supports this through page range queries) when request
  is successful. 
  - If request is unsuccessful, raw response object is always available 
  - `strerror` attribute (I think) contains extra information. 

General   
- Fix client liveness check. Currently the CICD pipeline is not running
  on schedule as intended. 
- Add pre-commit hook to 
  - run black code formatting 
