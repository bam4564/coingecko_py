# CoingeckoApi

All URIs are relative to *https://api.coingecko.com/api/v3*

Method | HTTP request | Description
------------- | ------------- | -------------
[**asset_platforms_get**](API.md#asset_platforms_get) | **GET** /asset_platforms | List all asset platforms (Blockchain networks)
[**coins_categories_get**](API.md#coins_categories_get) | **GET** /coins/categories | List all categories with market data
[**coins_categories_list_get**](API.md#coins_categories_list_get) | **GET** /coins/categories/list | List all categories
[**coins_id_contract_contract_address_get**](API.md#coins_id_contract_contract_address_get) | **GET** /coins/{id}/contract/{contract_address} | Get coin info from contract address
[**coins_id_contract_contract_address_market_chart_get**](API.md#coins_id_contract_contract_address_market_chart_get) | **GET** /coins/{id}/contract/{contract_address}/market_chart/ | Get historical market data include price, market cap, and 24h volume (granularity auto) from a contract address 
[**coins_id_contract_contract_address_market_chart_range_get**](API.md#coins_id_contract_contract_address_market_chart_range_get) | **GET** /coins/{id}/contract/{contract_address}/market_chart/range | Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto) from a contract address
[**coins_id_get**](API.md#coins_id_get) | **GET** /coins/{id} | Get current data (name, price, market, ... including exchange tickers) for a coin
[**coins_id_history_get**](API.md#coins_id_history_get) | **GET** /coins/{id}/history | Get historical data (name, price, market, stats) at a given date for a coin
[**coins_id_market_chart_get**](API.md#coins_id_market_chart_get) | **GET** /coins/{id}/market_chart | Get historical market data include price, market cap, and 24h volume (granularity auto)
[**coins_id_market_chart_range_get**](API.md#coins_id_market_chart_range_get) | **GET** /coins/{id}/market_chart/range | Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)
[**coins_id_ohlc_get**](API.md#coins_id_ohlc_get) | **GET** /coins/{id}/ohlc | Get coin&#x27;s OHLC
[**coins_id_status_updates_get**](API.md#coins_id_status_updates_get) | **GET** /coins/{id}/status_updates | Get status updates for a given coin
[**coins_id_tickers_get**](API.md#coins_id_tickers_get) | **GET** /coins/{id}/tickers | Get coin tickers (paginated to 100 items)
[**coins_list_get**](API.md#coins_list_get) | **GET** /coins/list | List all supported coins id, name and symbol (no pagination required)
[**coins_markets_get**](API.md#coins_markets_get) | **GET** /coins/markets | List all supported coins price, market cap, volume, and market related data
[**companies_public_treasury_coin_id_get**](API.md#companies_public_treasury_coin_id_get) | **GET** /companies/public_treasury/{coin_id} | Get public companies data
[**derivatives_exchanges_get**](API.md#derivatives_exchanges_get) | **GET** /derivatives/exchanges | List all derivative exchanges
[**derivatives_exchanges_id_get**](API.md#derivatives_exchanges_id_get) | **GET** /derivatives/exchanges/{id} | show derivative exchange data
[**derivatives_exchanges_list_get**](API.md#derivatives_exchanges_list_get) | **GET** /derivatives/exchanges/list | List all derivative exchanges name and identifier
[**derivatives_get**](API.md#derivatives_get) | **GET** /derivatives | List all derivative tickers
[**exchange_rates_get**](API.md#exchange_rates_get) | **GET** /exchange_rates | Get BTC-to-Currency exchange rates
[**exchanges_get**](API.md#exchanges_get) | **GET** /exchanges | List all exchanges
[**exchanges_id_get**](API.md#exchanges_id_get) | **GET** /exchanges/{id} | Get exchange volume in BTC and top 100 tickers only
[**exchanges_id_status_updates_get**](API.md#exchanges_id_status_updates_get) | **GET** /exchanges/{id}/status_updates | Get status updates for a given exchange
[**exchanges_id_tickers_get**](API.md#exchanges_id_tickers_get) | **GET** /exchanges/{id}/tickers | Get exchange tickers (paginated, 100 tickers per page)
[**exchanges_id_volume_chart_get**](API.md#exchanges_id_volume_chart_get) | **GET** /exchanges/{id}/volume_chart | Get volume_chart data for a given exchange
[**exchanges_list_get**](API.md#exchanges_list_get) | **GET** /exchanges/list | List all supported markets id and name (no pagination required)
[**finance_platforms_get**](API.md#finance_platforms_get) | **GET** /finance_platforms | List all finance platforms
[**finance_products_get**](API.md#finance_products_get) | **GET** /finance_products | List all finance products
[**global_decentralized_finance_defi_get**](API.md#global_decentralized_finance_defi_get) | **GET** /global/decentralized_finance_defi | Get cryptocurrency global decentralized finance(defi) data
[**global_get**](API.md#global_get) | **GET** /global | Get cryptocurrency global data
[**indexes_get**](API.md#indexes_get) | **GET** /indexes | List all market indexes
[**indexes_list_get**](API.md#indexes_list_get) | **GET** /indexes/list | list market indexes id and name
[**indexes_market_id_id_get**](API.md#indexes_market_id_id_get) | **GET** /indexes/{market_id}/{id} | get market index by market id and index id
[**ping_get**](API.md#ping_get) | **GET** /ping | Check API server status
[**search_get**](API.md#search_get) | **GET** /search | Search for coins, categories and markets on CoinGecko
[**search_trending_get**](API.md#search_trending_get) | **GET** /search/trending | Get trending search coins (Top-7) on CoinGecko in the last 24 hours
[**simple_price_get**](API.md#simple_price_get) | **GET** /simple/price | Get the current price of any cryptocurrencies in any other supported currencies that you need.
[**simple_supported_vs_currencies_get**](API.md#simple_supported_vs_currencies_get) | **GET** /simple/supported_vs_currencies | Get list of supported_vs_currencies.
[**simple_token_price_id_get**](API.md#simple_token_price_id_get) | **GET** /simple/token_price/{id} | Get current price of tokens (using contract addresses) for a given platform in any other currency that you need.
[**status_updates_get**](API.md#status_updates_get) | **GET** /status_updates | List all status_updates with data (description, category, created_at, user, user_title and pin)

# **asset_platforms_get**
> asset_platforms_get()

List all asset platforms (Blockchain networks)

List all asset platforms

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.asset_platforms_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_categories_get**
> coins_categories_get(order=order)

List all categories with market data

List all categories with market data

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
order = 'order_example' # str | valid values: <b>market_cap_desc (default), market_cap_asc, name_desc, name_asc, market_cap_change_24h_desc and market_cap_change_24h_asc</b> (optional)

res = cg.coins_categories_get(order=order)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order** | **str**| valid values: &lt;b&gt;market_cap_desc (default), market_cap_asc, name_desc, name_asc, market_cap_change_24h_desc and market_cap_change_24h_asc&lt;/b&gt; | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_categories_list_get**
> coins_categories_list_get()

List all categories

List all categories

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.coins_categories_list_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_contract_contract_address_get**
> coins_id_contract_contract_address_get(id, contract_address)

Get coin info from contract address

Get coin info from contract address

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | Asset platform (See asset_platforms endpoint for list of options)
contract_address = 'contract_address_example' # str | Token's contract address

res = cg.coins_id_contract_contract_address_get(id, contract_address)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Asset platform (See asset_platforms endpoint for list of options) | 
 **contract_address** | **str**| Token&#x27;s contract address | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_contract_contract_address_market_chart_get**
> coins_id_contract_contract_address_market_chart_get(id, contract_address, vs_currency, days)

Get historical market data include price, market cap, and 24h volume (granularity auto) from a contract address 

Get historical market data include price, market cap, and 24h volume (granularity auto) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | The id of the platform issuing tokens (See asset_platforms endpoint for list of options)
contract_address = 'contract_address_example' # str | Token's contract address
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
days = 'days_example' # str | Data up to number of days ago (eg. 1,14,30,max)

res = cg.coins_id_contract_contract_address_market_chart_get(id, contract_address, vs_currency, days)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The id of the platform issuing tokens (See asset_platforms endpoint for list of options) | 
 **contract_address** | **str**| Token&#x27;s contract address | 
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **days** | **str**| Data up to number of days ago (eg. 1,14,30,max) | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_contract_contract_address_market_chart_range_get**
> coins_id_contract_contract_address_market_chart_range_get(id, contract_address, vs_currency, _from, to)

Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto) from a contract address

Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | The id of the platform issuing tokens (See asset_platforms endpoint for list of options)
contract_address = 'contract_address_example' # str | Token's contract address
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
_from = '_from_example' # str | From date in UNIX Timestamp (eg. 1392577232)
to = 'to_example' # str | To date in UNIX Timestamp (eg. 1422577232)

res = cg.coins_id_contract_contract_address_market_chart_range_get(id, contract_address, vs_currency, _from, to)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The id of the platform issuing tokens (See asset_platforms endpoint for list of options) | 
 **contract_address** | **str**| Token&#x27;s contract address | 
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **_from** | **str**| From date in UNIX Timestamp (eg. 1392577232) | 
 **to** | **str**| To date in UNIX Timestamp (eg. 1422577232) | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_get**
> coins_id_get(id, localization=localization, tickers=tickers, market_data=market_data, community_data=community_data, developer_data=developer_data, sparkline=sparkline)

Get current data (name, price, market, ... including exchange tickers) for a coin

Get current data (name, price, market, ... including exchange tickers) for a coin.<br><br> **IMPORTANT**:  Ticker object is limited to 100 items, to get more tickers, use `/coins/{id}/tickers`  Ticker `is_stale` is true when ticker that has not been updated/unchanged from the exchange for a while.  Ticker `is_anomaly` is true if ticker's price is outliered by our system.  You are responsible for managing how you want to display these information (e.g. footnote, different background, change opacity, hide) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins) eg. bitcoin
localization = 'localization_example' # str | Include all localized languages in response (true/false) <b>[default: true]</b> (optional)
tickers = true # bool | Include tickers data (true/false) <b>[default: true]</b> (optional)
market_data = true # bool | Include market_data (true/false) <b>[default: true]</b> (optional)
community_data = true # bool | Include community_data data (true/false) <b>[default: true]</b> (optional)
developer_data = true # bool | Include developer_data data (true/false) <b>[default: true]</b> (optional)
sparkline = true # bool | Include sparkline 7 days data (eg. true, false) <b>[default: false]</b> (optional)

res = cg.coins_id_get(id, localization=localization, tickers=tickers, market_data=market_data, community_data=community_data, developer_data=developer_data, sparkline=sparkline)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins) eg. bitcoin | 
 **localization** | **str**| Include all localized languages in response (true/false) &lt;b&gt;[default: true]&lt;/b&gt; | [optional] 
 **tickers** | **bool**| Include tickers data (true/false) &lt;b&gt;[default: true]&lt;/b&gt; | [optional] 
 **market_data** | **bool**| Include market_data (true/false) &lt;b&gt;[default: true]&lt;/b&gt; | [optional] 
 **community_data** | **bool**| Include community_data data (true/false) &lt;b&gt;[default: true]&lt;/b&gt; | [optional] 
 **developer_data** | **bool**| Include developer_data data (true/false) &lt;b&gt;[default: true]&lt;/b&gt; | [optional] 
 **sparkline** | **bool**| Include sparkline 7 days data (eg. true, false) &lt;b&gt;[default: false]&lt;/b&gt; | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_history_get**
> coins_id_history_get(id, _date, localization=localization)

Get historical data (name, price, market, stats) at a given date for a coin

Get historical data (name, price, market, stats) at a given date for a coin 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins) eg. bitcoin
_date = '_date_example' # str | The date of data snapshot in dd-mm-yyyy eg. 30-12-2017
localization = 'localization_example' # str | Set to false to exclude localized languages in response (optional)

res = cg.coins_id_history_get(id, _date, localization=localization)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins) eg. bitcoin | 
 **_date** | **str**| The date of data snapshot in dd-mm-yyyy eg. 30-12-2017 | 
 **localization** | **str**| Set to false to exclude localized languages in response | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_market_chart_get**
> coins_id_market_chart_get(id, vs_currency, days, interval=interval)

Get historical market data include price, market cap, and 24h volume (granularity auto)

Get historical market data include price, market cap, and 24h volume (granularity auto)  <b>Minutely data will be used for duration within 1 day, Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.</b>

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins) eg. bitcoin
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
days = 'days_example' # str | Data up to number of days ago (eg. 1,14,30,max)
interval = 'interval_example' # str | Data interval. Possible value: daily (optional)

res = cg.coins_id_market_chart_get(id, vs_currency, days, interval=interval)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins) eg. bitcoin | 
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **days** | **str**| Data up to number of days ago (eg. 1,14,30,max) | 
 **interval** | **str**| Data interval. Possible value: daily | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_market_chart_range_get**
> coins_id_market_chart_range_get(id, vs_currency, _from, to)

Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)

Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)  <b><ul><li>Data granularity is automatic (cannot be adjusted)</li><li>1 day from query time = 5 minute interval data</li><li>1 - 90 days from query time = hourly data</li><li>above 90 days from query time = daily data (00:00 UTC)</li></ul> </b>

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins) eg. bitcoin
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
_from = '_from_example' # str | From date in UNIX Timestamp (eg. 1392577232)
to = 'to_example' # str | To date in UNIX Timestamp (eg. 1422577232)

res = cg.coins_id_market_chart_range_get(id, vs_currency, _from, to)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins) eg. bitcoin | 
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **_from** | **str**| From date in UNIX Timestamp (eg. 1392577232) | 
 **to** | **str**| To date in UNIX Timestamp (eg. 1422577232) | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_ohlc_get**
> list[float] coins_id_ohlc_get(id, vs_currency, days)

Get coin's OHLC

Candle's body:  1 - 2 days: 30 minutes 3 - 30 days: 4 hours 31 and before: 4 days

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins/list) eg. bitcoin
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
days = 56 # int |  Data up to number of days ago (1/7/14/30/90/180/365/max)

res = cg.coins_id_ohlc_get(id, vs_currency, days)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins/list) eg. bitcoin | 
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **days** | **int**|  Data up to number of days ago (1/7/14/30/90/180/365/max) | 

### Return type

**list[float]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_status_updates_get**
> coins_id_status_updates_get(id, per_page=per_page, page=page)

Get status updates for a given coin

Get status updates for a given coin

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins) eg. bitcoin
per_page = 56 # int | Total results per page (optional)
page = 56 # int | Page through results (optional)

res = cg.coins_id_status_updates_get(id, per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins) eg. bitcoin | 
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **int**| Page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_id_tickers_get**
> coins_id_tickers_get(id, exchange_ids=exchange_ids, include_exchange_logo=include_exchange_logo, page=page, order=order, depth=depth)

Get coin tickers (paginated to 100 items)

Get coin tickers (paginated to 100 items)<br><br> **IMPORTANT**:  Ticker `is_stale` is true when ticker that has not been updated/unchanged from the exchange for a while.  Ticker `is_anomaly` is true if ticker's price is outliered by our system.  You are responsible for managing how you want to display these information (e.g. footnote, different background, change opacity, hide) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the coin id (can be obtained from /coins/list) eg. bitcoin
exchange_ids = 'exchange_ids_example' # str | filter results by exchange_ids (ref: v3/exchanges/list) (optional)
include_exchange_logo = 'include_exchange_logo_example' # str | flag to show exchange_logo (optional)
page = 56 # int | Page through results (optional)
order = 'order_example' # str | valid values: <b>trust_score_desc (default), trust_score_asc and volume_desc</b> (optional)
depth = 'depth_example' # str | flag to show 2% orderbook depth. valid values: true, false (optional)

res = cg.coins_id_tickers_get(id, exchange_ids=exchange_ids, include_exchange_logo=include_exchange_logo, page=page, order=order, depth=depth)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the coin id (can be obtained from /coins/list) eg. bitcoin | 
 **exchange_ids** | **str**| filter results by exchange_ids (ref: v3/exchanges/list) | [optional] 
 **include_exchange_logo** | **str**| flag to show exchange_logo | [optional] 
 **page** | **int**| Page through results | [optional] 
 **order** | **str**| valid values: &lt;b&gt;trust_score_desc (default), trust_score_asc and volume_desc&lt;/b&gt; | [optional] 
 **depth** | **str**| flag to show 2% orderbook depth. valid values: true, false | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_list_get**
> coins_list_get(include_platform=include_platform)

List all supported coins id, name and symbol (no pagination required)

Use this to obtain all the coins' id in order to make API calls

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
include_platform = true # bool | flag to include platform contract addresses (eg. 0x.... for Ethereum based tokens).   valid values: true, false (optional)

res = cg.coins_list_get(include_platform=include_platform)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_platform** | **bool**| flag to include platform contract addresses (eg. 0x.... for Ethereum based tokens).   valid values: true, false | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **coins_markets_get**
> coins_markets_get(vs_currency, ids=ids, category=category, order=order, per_page=per_page, page=page, sparkline=sparkline, price_change_percentage=price_change_percentage)

List all supported coins price, market cap, volume, and market related data

Use this to obtain all the coins market data (price, market cap, volume)

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
vs_currency = 'vs_currency_example' # str | The target currency of market data (usd, eur, jpy, etc.)
ids = 'ids_example' # str | The ids of the coin, comma separated crytocurrency symbols (base). refers to `/coins/list`. <b>When left empty, returns numbers the coins observing the params `limit` and `start`</b> (optional)
category = 'category_example' # str | filter by coin category. Refer to /coin/categories/list (optional)
order = 'market_cap_desc' # str | valid values: <b>market_cap_desc, gecko_desc, gecko_asc, market_cap_asc, market_cap_desc, volume_asc, volume_desc, id_asc, id_desc</b> sort results by field. (optional) (default to market_cap_desc)
per_page = 100 # int | valid values: 1..250  Total results per page (optional) (default to 100)
page = 1 # int | Page through results (optional) (default to 1)
sparkline = false # bool | Include sparkline 7 days data (eg. true, false) (optional) (default to false)
price_change_percentage = 'price_change_percentage_example' # str | Include price change percentage in <b>1h, 24h, 7d, 14d, 30d, 200d, 1y</b> (eg. '`1h,24h,7d`' comma-separated, invalid values will be discarded) (optional)

res = cg.coins_markets_get(vs_currency, ids=ids, category=category, order=order, per_page=per_page, page=page, sparkline=sparkline, price_change_percentage=price_change_percentage)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vs_currency** | **str**| The target currency of market data (usd, eur, jpy, etc.) | 
 **ids** | **str**| The ids of the coin, comma separated crytocurrency symbols (base). refers to &#x60;/coins/list&#x60;. &lt;b&gt;When left empty, returns numbers the coins observing the params &#x60;limit&#x60; and &#x60;start&#x60;&lt;/b&gt; | [optional] 
 **category** | **str**| filter by coin category. Refer to /coin/categories/list | [optional] 
 **order** | **str**| valid values: &lt;b&gt;market_cap_desc, gecko_desc, gecko_asc, market_cap_asc, market_cap_desc, volume_asc, volume_desc, id_asc, id_desc&lt;/b&gt; sort results by field. | [optional] [default to market_cap_desc]
 **per_page** | **int**| valid values: 1..250  Total results per page | [optional] [default to 100]
 **page** | **int**| Page through results | [optional] [default to 1]
 **sparkline** | **bool**| Include sparkline 7 days data (eg. true, false) | [optional] [default to false]
 **price_change_percentage** | **str**| Include price change percentage in &lt;b&gt;1h, 24h, 7d, 14d, 30d, 200d, 1y&lt;/b&gt; (eg. &#x27;&#x60;1h,24h,7d&#x60;&#x27; comma-separated, invalid values will be discarded) | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **companies_public_treasury_coin_id_get**
> companies_public_treasury_coin_id_get(coin_id)

Get public companies data

Get public companies bitcoin or ethereum holdings (Ordered by total holdings descending)

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
coin_id = 'coin_id_example' # str | bitcoin or ethereum

res = cg.companies_public_treasury_coin_id_get(coin_id)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **coin_id** | **str**| bitcoin or ethereum | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **derivatives_exchanges_get**
> derivatives_exchanges_get(order=order, per_page=per_page, page=page)

List all derivative exchanges

List all derivative exchanges

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
order = 'order_example' # str | order results using following params name_asc，name_desc，open_interest_btc_asc，open_interest_btc_desc，trade_volume_24h_btc_asc，trade_volume_24h_btc_desc (optional)
per_page = 56 # int | Total results per page (optional)
page = 56 # int | Page through results (optional)

res = cg.derivatives_exchanges_get(order=order, per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order** | **str**| order results using following params name_asc，name_desc，open_interest_btc_asc，open_interest_btc_desc，trade_volume_24h_btc_asc，trade_volume_24h_btc_desc | [optional] 
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **int**| Page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **derivatives_exchanges_id_get**
> derivatives_exchanges_id_get(id, include_tickers=include_tickers)

show derivative exchange data

show derivative exchange data

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the exchange id (can be obtained from derivatives/exchanges/list) eg. bitmex
include_tickers = 'include_tickers_example' # str | ['all', 'unexpired'] - expired to show unexpired tickers, all to list all tickers, leave blank to omit tickers data in response (optional)

res = cg.derivatives_exchanges_id_get(id, include_tickers=include_tickers)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the exchange id (can be obtained from derivatives/exchanges/list) eg. bitmex | 
 **include_tickers** | **str**| [&#x27;all&#x27;, &#x27;unexpired&#x27;] - expired to show unexpired tickers, all to list all tickers, leave blank to omit tickers data in response | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **derivatives_exchanges_list_get**
> derivatives_exchanges_list_get()

List all derivative exchanges name and identifier

List all derivative exchanges name and identifier

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.derivatives_exchanges_list_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **derivatives_get**
> derivatives_get(include_tickers=include_tickers)

List all derivative tickers

List all derivative tickers

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
include_tickers = 'include_tickers_example' # str | ['all', 'unexpired'] - expired to show unexpired tickers, all to list all tickers, defaults to unexpired (optional)

res = cg.derivatives_get(include_tickers=include_tickers)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_tickers** | **str**| [&#x27;all&#x27;, &#x27;unexpired&#x27;] - expired to show unexpired tickers, all to list all tickers, defaults to unexpired | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchange_rates_get**
> exchange_rates_get()

Get BTC-to-Currency exchange rates

Get BTC-to-Currency exchange rates 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.exchange_rates_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_get**
> exchanges_get(per_page=per_page, page=page)

List all exchanges

List all exchanges

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
per_page = 56 # int | Valid values: 1...250 Total results per page Default value:: 100 (optional)
page = 'page_example' # str | page through results (optional)

res = cg.exchanges_get(per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **per_page** | **int**| Valid values: 1...250 Total results per page Default value:: 100 | [optional] 
 **page** | **str**| page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_id_get**
> exchanges_id_get(id)

Get exchange volume in BTC and top 100 tickers only

Get exchange volume in BTC and tickers<br><br> **IMPORTANT**:  Ticker object is limited to 100 items, to get more tickers, use `/exchanges/{id}/tickers`  Ticker `is_stale` is true when ticker that has not been updated/unchanged from the exchange for a while.  Ticker `is_anomaly` is true if ticker's price is outliered by our system.  You are responsible for managing how you want to display these information (e.g. footnote, different background, change opacity, hide) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the exchange id (can be obtained from /exchanges/list) eg. binance

res = cg.exchanges_id_get(id)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the exchange id (can be obtained from /exchanges/list) eg. binance | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_id_status_updates_get**
> exchanges_id_status_updates_get(id, per_page=per_page, page=page)

Get status updates for a given exchange

Get status updates for a given exchange

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the exchange id (can be obtained from /exchanges/list) eg. binance
per_page = 56 # int | Total results per page (optional)
page = 56 # int | Page through results (optional)

res = cg.exchanges_id_status_updates_get(id, per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the exchange id (can be obtained from /exchanges/list) eg. binance | 
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **int**| Page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_id_tickers_get**
> exchanges_id_tickers_get(id, coin_ids=coin_ids, include_exchange_logo=include_exchange_logo, page=page, depth=depth, order=order)

Get exchange tickers (paginated, 100 tickers per page)

Get exchange tickers (paginated)<br><br> **IMPORTANT**:  Ticker `is_stale` is true when ticker that has not been updated/unchanged from the exchange for a while.  Ticker `is_anomaly` is true if ticker's price is outliered by our system.  You are responsible for managing how you want to display these information (e.g. footnote, different background, change opacity, hide) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the exchange id (can be obtained from /exchanges/list) eg. binance
coin_ids = 'coin_ids_example' # str | filter tickers by coin_ids (ref: v3/coins/list) (optional)
include_exchange_logo = 'include_exchange_logo_example' # str | flag to show exchange_logo (optional)
page = 56 # int | Page through results (optional)
depth = 'depth_example' # str | flag to show 2% orderbook depth i.e., cost_to_move_up_usd and cost_to_move_down_usd (optional)
order = 'order_example' # str | valid values: <b>trust_score_desc (default), trust_score_asc and volume_desc</b> (optional)

res = cg.exchanges_id_tickers_get(id, coin_ids=coin_ids, include_exchange_logo=include_exchange_logo, page=page, depth=depth, order=order)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the exchange id (can be obtained from /exchanges/list) eg. binance | 
 **coin_ids** | **str**| filter tickers by coin_ids (ref: v3/coins/list) | [optional] 
 **include_exchange_logo** | **str**| flag to show exchange_logo | [optional] 
 **page** | **int**| Page through results | [optional] 
 **depth** | **str**| flag to show 2% orderbook depth i.e., cost_to_move_up_usd and cost_to_move_down_usd | [optional] 
 **order** | **str**| valid values: &lt;b&gt;trust_score_desc (default), trust_score_asc and volume_desc&lt;/b&gt; | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_id_volume_chart_get**
> exchanges_id_volume_chart_get(id, days)

Get volume_chart data for a given exchange

Get volume_chart data for a given exchange

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | pass the exchange id (can be obtained from /exchanges/list) eg. binance
days = 56 # int |  Data up to number of days ago (eg. 1,14,30)

res = cg.exchanges_id_volume_chart_get(id, days)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| pass the exchange id (can be obtained from /exchanges/list) eg. binance | 
 **days** | **int**|  Data up to number of days ago (eg. 1,14,30) | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **exchanges_list_get**
> exchanges_list_get()

List all supported markets id and name (no pagination required)

Use this to obtain all the markets' id in order to make API calls

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.exchanges_list_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **finance_platforms_get**
> finance_platforms_get(per_page=per_page, page=page)

List all finance platforms

List all finance platforms

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
per_page = 56 # int | Total results per page (optional)
page = 'page_example' # str | page of results (paginated to 100 by default) (optional)

res = cg.finance_platforms_get(per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **str**| page of results (paginated to 100 by default) | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **finance_products_get**
> finance_products_get(per_page=per_page, page=page, start_at=start_at, end_at=end_at)

List all finance products

List all finance products

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
per_page = 56 # int | Total results per page (optional)
page = 'page_example' # str | page of results (paginated to 100 by default) (optional)
start_at = 'start_at_example' # str | start date of the financial products (optional)
end_at = 'end_at_example' # str | end date of the financial products (optional)

res = cg.finance_products_get(per_page=per_page, page=page, start_at=start_at, end_at=end_at)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **str**| page of results (paginated to 100 by default) | [optional] 
 **start_at** | **str**| start date of the financial products | [optional] 
 **end_at** | **str**| end date of the financial products | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **global_decentralized_finance_defi_get**
> global_decentralized_finance_defi_get()

Get cryptocurrency global decentralized finance(defi) data

Get Top 100 Cryptocurrency Global Eecentralized Finance(defi) data 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.global_decentralized_finance_defi_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **global_get**
> global_get()

Get cryptocurrency global data

Get cryptocurrency global data 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.global_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **indexes_get**
> indexes_get(per_page=per_page, page=page)

List all market indexes

List all market indexes

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
per_page = 56 # int | Total results per page (optional)
page = 56 # int | Page through results (optional)

res = cg.indexes_get(per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **int**| Page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **indexes_list_get**
> indexes_list_get()

list market indexes id and name

list market indexes id and name

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.indexes_list_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **indexes_market_id_id_get**
> indexes_market_id_id_get(market_id, id)

get market index by market id and index id

get market index by market id and index id

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
market_id = 'market_id_example' # str | pass the market id (can be obtained from /exchanges/list)
id = 'id_example' # str | pass the index id (can be obtained from /indexes/list)

res = cg.indexes_market_id_id_get(market_id, id)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **market_id** | **str**| pass the market id (can be obtained from /exchanges/list) | 
 **id** | **str**| pass the index id (can be obtained from /indexes/list) | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ping_get**
> ping_get()

Check API server status

Check API server status 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.ping_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_get**
> search_get(query)

Search for coins, categories and markets on CoinGecko

Search for coins, categories and markets listed on CoinGecko ordered by largest Market Cap first

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
query = 'query_example' # str | Search string

res = cg.search_get(query)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| Search string | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_trending_get**
> search_trending_get()

Get trending search coins (Top-7) on CoinGecko in the last 24 hours

Top-7 trending coins on CoinGecko as searched by users in the last 24 hours (Ordered by most popular first)

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.search_trending_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **simple_price_get**
> simple_price_get(ids, vs_currencies, include_market_cap=include_market_cap, include_24hr_vol=include_24hr_vol, include_24hr_change=include_24hr_change, include_last_updated_at=include_last_updated_at)

Get the current price of any cryptocurrencies in any other supported currencies that you need.

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
ids = 'ids_example' # str | id of coins, comma-separated if querying more than 1 coin *refers to <b>`coins/list`</b>
vs_currencies = 'vs_currencies_example' # str | vs_currency of coins, comma-separated if querying more than 1 vs_currency *refers to <b>`simple/supported_vs_currencies`</b>
include_market_cap = 'include_market_cap_example' # str | <b>true/false</b> to include market_cap, <b>default: false</b> (optional)
include_24hr_vol = 'include_24hr_vol_example' # str | <b>true/false</b> to include 24hr_vol, <b>default: false</b> (optional)
include_24hr_change = 'include_24hr_change_example' # str | <b>true/false</b> to include 24hr_change, <b>default: false</b> (optional)
include_last_updated_at = 'include_last_updated_at_example' # str | <b>true/false</b> to include last_updated_at of price, <b>default: false</b> (optional)

res = cg.simple_price_get(ids, vs_currencies, include_market_cap=include_market_cap, include_24hr_vol=include_24hr_vol, include_24hr_change=include_24hr_change, include_last_updated_at=include_last_updated_at)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ids** | **str**| id of coins, comma-separated if querying more than 1 coin *refers to &lt;b&gt;&#x60;coins/list&#x60;&lt;/b&gt; | 
 **vs_currencies** | **str**| vs_currency of coins, comma-separated if querying more than 1 vs_currency *refers to &lt;b&gt;&#x60;simple/supported_vs_currencies&#x60;&lt;/b&gt; | 
 **include_market_cap** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include market_cap, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_24hr_vol** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include 24hr_vol, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_24hr_change** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include 24hr_change, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_last_updated_at** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include last_updated_at of price, &lt;b&gt;default: false&lt;/b&gt; | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **simple_supported_vs_currencies_get**
> simple_supported_vs_currencies_get()

Get list of supported_vs_currencies.

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()

res = cg.simple_supported_vs_currencies_get()
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **simple_token_price_id_get**
> simple_token_price_id_get(id, contract_addresses, vs_currencies, include_market_cap=include_market_cap, include_24hr_vol=include_24hr_vol, include_24hr_change=include_24hr_change, include_last_updated_at=include_last_updated_at)

Get current price of tokens (using contract addresses) for a given platform in any other currency that you need.

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
id = 'id_example' # str | The id of the platform issuing tokens (See asset_platforms endpoint for list of options)
contract_addresses = 'contract_addresses_example' # str | The contract address of tokens, comma separated
vs_currencies = 'vs_currencies_example' # str | vs_currency of coins, comma-separated if querying more than 1 vs_currency *refers to <b>`simple/supported_vs_currencies`</b>
include_market_cap = 'include_market_cap_example' # str | <b>true/false</b> to include market_cap, <b>default: false</b> (optional)
include_24hr_vol = 'include_24hr_vol_example' # str | <b>true/false</b> to include 24hr_vol, <b>default: false</b> (optional)
include_24hr_change = 'include_24hr_change_example' # str | <b>true/false</b> to include 24hr_change, <b>default: false</b> (optional)
include_last_updated_at = 'include_last_updated_at_example' # str | <b>true/false</b> to include last_updated_at of price, <b>default: false</b> (optional)

res = cg.simple_token_price_id_get(id, contract_addresses, vs_currencies, include_market_cap=include_market_cap, include_24hr_vol=include_24hr_vol, include_24hr_change=include_24hr_change, include_last_updated_at=include_last_updated_at)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The id of the platform issuing tokens (See asset_platforms endpoint for list of options) | 
 **contract_addresses** | **str**| The contract address of tokens, comma separated | 
 **vs_currencies** | **str**| vs_currency of coins, comma-separated if querying more than 1 vs_currency *refers to &lt;b&gt;&#x60;simple/supported_vs_currencies&#x60;&lt;/b&gt; | 
 **include_market_cap** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include market_cap, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_24hr_vol** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include 24hr_vol, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_24hr_change** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include 24hr_change, &lt;b&gt;default: false&lt;/b&gt; | [optional] 
 **include_last_updated_at** | **str**| &lt;b&gt;true/false&lt;/b&gt; to include last_updated_at of price, &lt;b&gt;default: false&lt;/b&gt; | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **status_updates_get**
> status_updates_get(category=category, project_type=project_type, per_page=per_page, page=page)

List all status_updates with data (description, category, created_at, user, user_title and pin)

List all status_updates with data (description, category, created_at, user, user_title and pin) 

### Example
```python
from py_coingecko import CoingeckoApi

# create an instance of the API class
cg = CoingeckoApi()
category = 'category_example' # str | Filtered by category (eg. general, milestone, partnership, exchange_listing, software_release, fund_movement, new_listings, event) (optional)
project_type = 'project_type_example' # str | Filtered by Project Type (eg. coin, market). If left empty returns both status from coins and markets. (optional)
per_page = 56 # int | Total results per page (optional)
page = 56 # int | Page through results (optional)

res = cg.status_updates_get(category=category, project_type=project_type, per_page=per_page, page=page)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category** | **str**| Filtered by category (eg. general, milestone, partnership, exchange_listing, software_release, fund_movement, new_listings, event) | [optional] 
 **project_type** | **str**| Filtered by Project Type (eg. coin, market). If left empty returns both status from coins and markets. | [optional] 
 **per_page** | **int**| Total results per page | [optional] 
 **page** | **int**| Page through results | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

