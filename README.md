# coingecko_py 

![Api Version](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/brycemorrow4564/e454b900fe6518d21bdd25c9508d8a64/raw/coingecko_py_apiversion__heads_master.json)
![Api Updated](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/brycemorrow4564/e454b900fe6518d21bdd25c9508d8a64/raw/coingecko_py_clientupdated__heads_master.json)
![Tests](https://github.com/brycemorrow4564/coingecko_py/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/brycemorrow4564/e454b900fe6518d21bdd25c9508d8a64/raw/coingecko_py__heads_master.json)

[![PyPi Version](https://img.shields.io/pypi/v/coingecko_py.svg)](https://pypi.org/project/coingecko_py/)
![GitHub](https://img.shields.io/github/license/brycemorrow4564/coingecko_py)

## An Advanced API Client For The Coingecko API

The base api client class and its documentation are automatically generated with [`swagger-codegen`](https://swagger.io/tools/swagger-codegen/) from the OpenAPI specification available [here](https://www.coingecko.com/api/documentations/v3/swagger.json) on the coingecko website. 

> The documentation for the api client can be found [here](./docs/API.md). 

This ensures that all endpoints and their corresponding parameters are **100%** correct. Furthermore, 
the "Client Updated" badge you see at the top of this README is a live check that the spec used to 
generate the client code matches the latest version of the spec available on the coingecko website. 
This badge is updated once a day as a part of the CICD pipeline. 

Additionally, the base api client has been extended to provide additional functionality like

- Abstracting away complexities associated with server side rate limiting when sending many api requests. 
- Page range queries (bounded and unbounded). 

## Outline 

[Installation](#installation)

[Usage](#usage)

[API Reference](./docs/API.md)

[Advanced Features - Mitigate Rate Limiting](#advanced-features---mitigate-rate-limiting)

[Advanced Features - Page Range Queries](#advanced-features---page-range-queries)

[Client Configuration](#client-configuration)

[Summary](#summary)

[Development and Testing](#development-and-testing)

[License](#license)

## Installation 

This package is currently only available through **PyPI**. You can install 
it by running

```shell
pip install coingecko_py
```

## Usage 

This package exposes a single class called `CoingeckoApi`. To import and 
initialize this class, do the following

```python
from coingecko_py import CoingeckoApi
cg = CoingeckoApi()
```

Check out the [API Reference](./docs/API.md) for more details on how
to use this object. 

## Advanced Features  

This section includes usage examples for advanced features that have been added to the 
base api client. 

### Advanced Features - Mitigate Rate Limiting  

> Note: This functionality is available for **all** endpoints available on the base client.

Imagine you wanted to get price data for the last year on the top 1000 market cap coins. 

First, we get the data for the top 1000 market cap coins. Each page returns 100 results and pages are already sorted by market cap. 
```python
# np.ravel flattens a list of lists
import numpy as np 
coins = np.ravel([cg.coins_markets_get('usd', page=i) for i in range(1, 11)])
```

Next, we iterate over `coins` and use each coin id to query for it's price data. 

```python
ndays = 365
prices = dict()
for c in coins: 
    cid = c['id']
    prices[cid] = cg.coins_id_market_chart_get(cid, 'usd', ndays)['prices']
```
The issue here is that the coingecko api performs server side rate limiting. If you are using the free tier, it's about 50 api calls per second. Paid tiers have higher limits, but there is still a limit. 

Since the above code block would be sending 1000 api requests synchronously, it is likely to fail at some point if you have a decent internet connection. In order to get around this, you would have to add error detection and call management logic. If you are writing a complex app with many api calls, this can be really annoying. 

The **coingecko_py** client introduces a mechanism to queue api calls and execute a series of queued calls while performing **client side exponential backoff retries**. See [here](https://docs.aws.amazon.com/general/latest/gr/api-retries.html) for an explanation of this strategy. 

This allows you to write code without worrying about rate limiting! Here is a block of code that is equivalent to the above code block that won't error out due to rate limiting. 

```python 
ndays = 365
for c in coins: 
    cid = c['id']
    cg.coins_id_market_chart_get(cid, 'usd', ndays, qid=cid)
prices = cg.execute_queued()
prices = {k: v['prices'] for k, v in prices.items()}
```

The key differences here are 

- The inclusion of the `qid` keyword argument in the api call signature. 
  - `qid` stands for queue id. 
  - Whenever `qid` is present as a keyword argument in an api call, the client will queue the call instead of executing it. 
  - `qid` can be used as a lookup key for the result of this api call once it is executed. 
  
- The line containing the api call (`cg.coins_id_market_chart_get(...)`) does not return anything. 
  - Whenever `qid` is not a kwarg, an api call behaves exactly the same as the base api client. 
  - Whenever `qid` is a kwarg, an api call returns nothing, as it was queued. 
  
- The function `execute_queued` must be invoked in order to execute all queued calls. 
  - It internally deals with rate limiting. 
  - It's return value is a dictionary where the keys are the `qid` values from queued calls and the values are the data parsed from responses of the corresponding api calls. 
  - If `execute_queued` is successful, the internal call queue is cleared. 
    - So if you called `execute_queued` on line 1 then again on line 2, the second call would return an empty dictionary. 

These two blocks of code both produce a dictionary `prices` with the same exact structure (assuming the first code block doesn't error out because of rate limiting). 

```python 
prices = {
    'bitcoin': {
        'prices': [
            [1610236800000, 40296.5290038294],
            [1610323200000, 38397.895985418174],
            [1610409600000, 35669.90668663349],
            ...
        ]
    }, 
    'ethereum': {
        'prices': [
            [1610236800000, 1282.979575527323],
            [1610323200000, 1267.7310031512136],
            [1610409600000, 1092.9143378806064],
            ...
        ]
    },
    ...
} 
```

This approach to API design was loosely inspired by [dask's][https://docs.dask.org/en/stable/] approach to lazy execution of a sequence of operations on dataframes.

### Advanced Features - Page Range Queries 

> Note: This functionality is available for **all** endpoints the base client that support paging. 

The coingecko api has a number of endpoints that support pagination. Pagination is a common api feature where you can request a specific page of data from an api. This is often necessary as some data objects are too large to return in a single api response. If you want all the data for a particular api call you are executing, you must request data from all pages. 

Here is an example that uses the client to query for a single page of data

```python
cg.coins_id_tickers_get('bitcoin', page=2, per_page=50)
```

Page range queries allow you to request a range of pages in a **single** client call. The 
api client supports **bounded** and **unbounded** page range queries. 

- **Bounded** queries request pages over a fully defined range `[page_start, page_end]`. 
- **Unbounded** queries only require the specification of `page_start` and will return 
  data from all available pages from `page_start` onwards. 

For the code blocks below, let's assume we magically know there are 100 data pages for the `coins_id_tickers_get` endpoint for the given set of parameters. In reality, if you wanted 
to determine the number of data pages for a client call, you would need to make the call, 
inspect the HTTP headers, perform a calculation to determine the total number of pages, 
then loop over the page range and make a request per each page. 

Here is an example of doing pagination manually using the base api client functionality 

```python 
data = []
for i in range(1, 101):
    res = cg.coins_id_tickers_get('bitcoin', page=i)
    data.append(res)
```

Here is an example of doing a **bounded** page range query with the extended client.

```python 
cg.coins_id_tickers_get('bitcoin', qid="data", page_start=1, page_end=100)
data = cg.execute_queued()['data']
```

Here is an example of doing an **unbounded** page range query with the extended client.

```python 
cg.coins_id_tickers_get('bitcoin', qid="data", page_start=1)
data = cg.execute_queued()['data']
```

All code blocks will produce equivalent output. The return value of a page range query is a list of response data from each individual api call. So `data[0]` contains the result for page 1, `data[49]` contains the result for page 50.

It's important to note that `qid` must be included as a keyword argument for page range queries. 
Thus, page range queries will also automatically deal with rate limiting as detailed in the 
[rate limiting](#advanced-features---mitigate-rate-limiting) section. 

## Client Configuration

The extended client supports multiple configuration options which impact its behavior. 

| Kwarg | Default | Description | 
| --- | --- | --- |
| exp_limit | `8` | Max exponent (2<sup>exp_limit</sup>) for exponential backoff retries |
| progress_interval | `10` | Min percentage interval at which to log progress of queued api calls |
| log_level | `logging.INFO` | python [logging](https://docs.python.org/3/library/logging.html) log level for client log messages |

The API client doesn't print any messages, but has logs at the following levels. 
- 10 (`logging.DEBUG`) will provide logs about internal state of client. 
- 20 (`logging.INFO`) progress logs and other useful info exists at this level. 
- 30 (`logging.WARNING`) useful warnings. I don't recommend any level higher than this. 
See [here](https://docs.python.org/3/library/logging.html#levels) for more info on log levels. 

Here's an example of how to configure the client with non-default values. 
```python 
cg = CoingeckoApi(log_level=10, exp_limit=6, progress_interval=5)
```

## Summary 

A quick summary of the functionality offered by this package

- It's base api client is automatically generated, ensuring correctness. 
  - It's functionality is described in the [API Reference](./docs/API.md). 
- It's extra features are accessible in the following ways 
  - `cg.execute_queued` is the only public method added to the client. It takes no input arguments and returns a dictionary that maps `qid` values to the corresponding queued api call. 
  - You can queue api calls by include the keyword argument `qid` in a client call. When you include the kwarg `qid` the function call does not return anything (as it was queued for later execution). 
  - Queued calls benefit from the clients internal strategy for mitigating server side rate limiting. 
  - Page range queries allow you to request a range of data pages in a single client call. 
    - If `page_start` and `page_end` are both defined, it will return all data pages in range. 
    - If `page_start` is defined and `page_end` is not, it will return all data pages from `page_start` onwards.
    - Page range queries must be queued (include `qid` in their call signature). 

## Development and Testing 

This package is packaged with [poetry](https://python-poetry.org/)

If you have poetry installed, you can perform the following steps to set up the development environment. 

```shell 
git clone https://github.com/brycemorrow4564/coingecko_py.git
cd coingecko_py
poetry shell 
poetry update 
poetry install 
```

If you want to run the tests (within the dev environment), do the following 
```shell
poetry run test 
```

## License
[MIT](https://choosealicense.com/licenses/mit/)