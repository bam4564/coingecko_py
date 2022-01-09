# pycoingecko-extra 

An extension of the [**pycoingecko**](https://github.com/man-c/pycoingecko) api client that adds additional functionality like: 
- Abstracting away complexities associated with rate limiting that occurs when sending many api requests. 
- Enhanced pagination support (in-progress)
- Call parallelization (future work)
  
This module is intended to serve as a drop-in replacement for the pycoingecko api client and the additional functionality can be enabled as desired. 

## Usage 
To switch from the base api client to this augmented version, all you need to do is change
```python
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
```
to 
```python
from pycoingecko_extra import CoinGeckoAPIExtra
cg = CoinGeckoAPIExtra()
```
If you make this change to an existing script, it will function exactly the same as before, as `CoinGeckoAPIExtra` is a subclass of `CoinGeckoAPI`. 

## Examples - Rate Limiting  

**Note:** This rate limiting bypass functionality is available for **all** endpoints that the base api endpoint supports 

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
The issue here is that the coingecko api performs server side rate limiting. If you are using the free tier, it's about 50 api calls per second. Their paid tiers have higher limits, but there is still a limit. 

Since the above code block would be sending 1000 api requests synchronously, it is likely to fail at some point if you have a decent internet connection. In order to get around this, you would have to add error detection and call management logic. If you are writing a complex app with many api calls, this can be really annoying. 

The **pycoingecko_extra** client introduces a mechanism to queue api calls and execute a series of queued calls while performing client side exponential backoff retries. See [here](https://docs.aws.amazon.com/general/latest/gr/api-retries.html) for an explanation of this strategy. 

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
- The inclusion of the `qid` keyword argument in the api call signature. `qid` stands for queue id. Whenever `qid` is present as a keyword argument in an api call, the client will queue the call instead of executing it. `qid` can be used as a lookup key for the result of this api call once it is executed. 
- The line containing the api call (i.e. `cg.get_coin_market_chart_by_id(...)`) does not return anything. Whenever `qid` is a kwarg, an api call returns nothing. Whenever `qid` is not a kwarg, an api call behaves normally. 
- The function `execute_queued` must be invoked in order to execute all queued calls. It internally deals with rate limiting. It's return value is a dictionary where the keys are the `qid` values from queued calls and the values are the responses from the corresponding api calls. If `execute_queued` is successful, the call queue is cleared. 

These two blocks of code both produce a dictionary `prices` with the same exact structure (assuming the first code block didn't error out because of rate limiting). 

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
