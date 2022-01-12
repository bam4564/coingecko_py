1.0.0 / 2022-01-11
==================
* Added support for page range queries 
* Code cleanup on client class 
* Overhaul of testing architecture. Created script for fetching real data from api, then using this to populate mock endpoints within unit tests.

0.4.1 / 2022-01-09
==================
* Fixed issue where logging was to stderr not stdout.

0.4.0 / 2022-01-09
==================
* Rate limiting bypass via exponential backoff retries.  
* CICD and packaging infrastructure. 