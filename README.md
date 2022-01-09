# pycoingecko-extra 

An extension of the [**pycoingecko**](https://github.com/man-c/pycoingecko) api client that adds additional functionality like: 
- Abstracting away complexities associated with rate limiting that occurs when sending a high volume of api requests. 
- Enhanced pagination support (in-progress)
  
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
If you make this change to an existing script, it will function exactly the same as before. 

## Example - Rate Limiting 
Imagine you wanted to get price data for the last year on the top 1000 market cap coins. 

First, we get the data for the top 1000 market cap coins, namely their id which we can use to query the prices endpoint
```python
import numpy as np 
# coins are already sorted by market cap when returned from api 
# np.ravel flattens a list of lists
coins = np.ravel([cg.get_coins_markets('usd', page=i) for i in range(1, 11)])
ncoins = len(coins)
assert ncoins == 1000
```
Next, we iterate over `coins` and use each coin id to query for it's price data. Normally, you would do this the following way: 
```python
ndays = 365
prices = dict()
for c in coins: 
    cid = c['id']
    prices[cid] = cg.get_coin_market_chart_by_id(cid, 'usd', ndays)
```
The issue here is that the coingecko api performs server side rate limiting. If you are using the free tier, it's about 50 api calls per second. Their paid tiers have higher limits, but there is still a limit. 

Since the above code block would be sending 1000 api requests synchronously, it is likely to fail at some point if you have a decent internet connection. In order to get around this, you would have to add error detection and call management logic. If you are writing a complex app with many api calls, this can be really annoying. 

The **pycoingecko_extra** client introduces a mechanism to queue api calls and execute a series of queued calls while performing client side exponential backoff retries. See [here](https://docs.aws.amazon.com/general/latest/gr/api-retries.html) for an explanation of this strategy. 

This allows you to write code without logic that manages the possibility that you are going to get rate limited. Here is a block of code that is equivalent to the above code block, but will not error out due to rate limiting. 

```python 
ndays = 365
for c in coins: 
    cid = c['id']
    cg.get_coin_market_chart_by_id(cid, 'usd', ndays, qid=cid)
prices = cg.execute_queued()
```

The key differences here are 
- The inclusion of the `qid` keyword argument in the api call signature. `qid` stands for queue id and can be used as a lookup key for the result of this api call once it is executed. Note that api calls are not executed until `execute_queued` is invoked. 
- The line containing the api call (the line that begins with `cg.get_coin_market_chart_by_id`) does not return anything. 
- The function `execute_queued` must be invoked. It handles executing all queued calls and deals with the rate limiting. It's return value is a dictionary where the keys are the `qid` values from all queued calls and the corresponding value is the response from the api call. 

These two blocks of code both produce a dictionary `prices` with the same exact structure (assuming the first code block didn't error out because of rate limiting). 

This approach to API design was inspired by the [dask][https://docs.dask.org/en/stable/] project. I believe this extension makes it a lot easier to write complex scripts leveraging the coingecko api and I hope you do too! 

