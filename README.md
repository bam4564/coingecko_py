# py_coingecko 

[![PyPi Version](https://img.shields.io/pypi/v/py_coingecko.svg)](https://pypi.org/project/py_coingecko/)
![GitHub](https://img.shields.io/github/license/brycemorrow4564/py_coingecko)
![Tests](https://github.com/brycemorrow4564/py_coingecko/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/brycemorrow4564/e454b900fe6518d21bdd25c9508d8a64/raw/py_coingecko__heads_auto-gen.json)


An extension of the [**pycoingecko**](https://github.com/man-c/pycoingecko) api client that adds additional functionality like: 

- Abstracting away complexities associated with server side rate limiting when sending many api requests. 
- Page range queries. 
- Configurable temporal granularity (future work)
  
This module is intended to serve as a drop-in replacement for the pycoingecko api client and the additional functionality can be enabled as desired. 

To give users confidence that this is true, the unit tests for this package clone the tests from the base package, replace all instances of the base class with this modules' subclass, and include these tests in the full test suite (which includes robust tests for new features). 

## Outline 

[Installation](#installation)

[Usage](#usage)

[Examples - Mitigate Rate Limiting](#examples---mitigate-rate-limiting)

[Examples - Page Range Queries](#examples---page-range-queries)

[Client Configuration](#client-configuration)

[Summary](#summary)

[Development and Testing](#development-and-testing)

[License](#license)

## Installation 

PyPI
```shell
pip install py_coingecko
```

## Usage 

To switch from the base api client to this augmented version, all you need to do is change
```python
from pycoingecko import CoingeckoApi
cg = CoingeckoApi()
```
to 
```python
from py_coingecko import CoinGeckoAPIExtra
cg = CoinGeckoAPIExtra()
```
If you make this change to an existing script, it will function exactly the same as before as `CoinGeckoAPIExtra` is a subclass of `CoingeckoApi`. 

## Examples  

All references to `cg` that you see in code blocks within this section are an instance of `CoinGeckoAPIExtra`. 

### Examples - Mitigate Rate Limiting  

*Note: This functionality is available for **all** endpoints available on the base client.*

Imagine you wanted to get price data for the last year on the top 1000 market cap coins. 

First, we get the data for the top 1000 market cap coins. Each page returns 100 results and pages are already sorted by market cap. 
```python
# np.ravel flattens a list of lists
import numpy as np 
coins = np.ravel([cg.get_coins_markets('usd', page=i) for i in range(1, 11)])
```
Next, we iterate over `coins` and use each coin id to query for it's price data. Normally, you would do this the following way: 
```python
ndays = 365
prices = dict()
for c in coins: 
    cid = c['id']
    prices[cid] = cg.get_coin_market_chart_by_id(cid, 'usd', ndays)['prices']
```
The issue here is that the coingecko api performs server side rate limiting. If you are using the free tier, it's about 50 api calls per second. Paid tiers have higher limits, but there is still a limit. 

Since the above code block would be sending 1000 api requests synchronously, it is likely to fail at some point if you have a decent internet connection. In order to get around this, you would have to add error detection and call management logic. If you are writing a complex app with many api calls, this can be really annoying. 

The **py_coingecko** client introduces a mechanism to queue api calls and execute a series of queued calls while performing **client side exponential backoff retries**. See [here](https://docs.aws.amazon.com/general/latest/gr/api-retries.html) for an explanation of this strategy. 

This allows you to write code without worrying about rate limiting! Here is a block of code that is equivalent to the above code block that won't error out due to rate limiting. 

```python 
ndays = 365
for c in coins: 
    cid = c['id']
    cg.get_coin_market_chart_by_id(cid, 'usd', ndays, qid=cid)
prices = cg.execute_queued()
prices = {k: v['prices'] for k, v in prices.items()}
```

The key differences here are 

- The inclusion of the `qid` keyword argument in the api call signature. 
  - `qid` stands for queue id. 
  - Whenever `qid` is present as a keyword argument in an api call, the client will queue the call instead of executing it. 
  - `qid` can be used as a lookup key for the result of this api call once it is executed. 
  
- The line containing the api call (`cg.get_coin_market_chart_by_id(...)`) does not return anything. 
  - Whenever `qid` is not a kwarg, an api call behaves exactly the same as the base api client. 
  - Whenever `qid` is a kwarg, an api call returns nothing. 
  
- The function `execute_queued` must be invoked in order to execute all queued calls. 
  - It internally deals with rate limiting. 
  - It's return value is a dictionary where the keys are the `qid` values from queued calls and the values are the responses from the corresponding api calls. 
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

### Examples - Page Range Queries 

The coingecko api has a number of endpoints that support pagination. Pagination is a common api feature where you can request a specific page of data from an api. This is often necessary as some data objects are too large to return in a single api response. If you want all the data for a particular api call you are executing, you must request data from all pages. 

Here is an example that uses the client to query for a single page of data 
```python
cg.get_coin_ticker_by_id('bitcoin', page=2, per_page=50)
```

Page range queries allow you to request a range of pages in a **single** client call.

Here is an example of doing pagination using the base api client functionality 
```python 
data = []
for i in range(1, 101):
    res = cg.get_coin_ticker_by_id('bitcoin', page=i)
    data.append(res)
```

Here is an example of doing a page range query with the extended client
```python 
cg.get_coin_ticker_by_id('bitcoin', qid="data", page_start=1, page_end=100)
data = cg.execute_queued()['data']
```

Both code blocks produce equivalent output. The return value of a page range query is a list of response data from each individual api call. So `data[0]` contains the result for page 1, `data[49]` contains the result for page 50.

It's important to note that `qid` must be included as a keyword argument for page range queries. Thus, page range queries will also automatically deal with rate limiting as detailed in the [rate limiting](#examples---rate-limiting) section. 

The coolest thing about page range queries is that you can perform them without specifying a `page_end`. This will result in the retrival of all available data pages from `page_start` onwards. 
```python 
cg.get_coin_ticker_by_id('bitcoin', qid="data", page_start=1)
data = cg.execute_queued()['data']
```

This is actually hard to simulate with the base api client itself. For each of it's api endpoints methods, it only returns the data. It discards the HTTP response that includes headers which give users details about how many total pages exist. Using the base client, you would continually need to increment a counter and continue requesting pages until you found an empty data object. But since the api returns different types of data objects for different paginated endpoints (dict, list, etc.), you would need to have a different **empty** condition for different paginated endpoints.  

## Client Configuration

The extended client supports multiple configuration options which impact its behavior. 

| Kwarg | Default | Description | 
| --- | --- | --- |
| exp_limit | 8 | Max exponent (2<sup>exp_limit</sup>) for exponential backoff retries. |
| progress_interval | 10 | Min percent interval at which to log progress of queued api calls |
| log_level | 20 | python [logging](https://docs.python.org/3/library/logging.html) log level for client log messages |

The API client doesn't print any messages, but has logs at the following levels. 
- 10 (`logging.DEBUG`) will provide logs about internal state of client. 
- 20 (`logging.INFO`) progress logs and other useful info exists at this level. 
- 30 (`logging.WARNING`) useful warnings. I don't recommend any level higher than this. 
See [here](https://docs.python.org/3/library/logging.html#levels) for more info on log levels. 

Here's an example of how to configure the client with non-default values. 
```python 
cg = CoinGeckoAPIExtra(log_level=10, exp_limit=6, progress_interval=5)
```

## Summary 

To summarize all the above functionality of this package in a single section 

- `CoinGeckoAPIExtra` is an extended version of `CoingeckoApi` that can serve as a drop in replacement. 
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
git clone https://github.com/brycemorrow4564/py_coingecko.git
cd py_coingecko
poetry shell 
poetry update 
```

If you want to run the tests (within the dev environment), do the following 
```shell
poetry run test 
```

## License
[MIT](https://choosealicense.com/licenses/mit/)