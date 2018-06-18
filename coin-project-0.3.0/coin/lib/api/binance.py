# -*- coding=utf-8 -*-
import hashlib
import hmac
import requests
import six
import time
from coin.lib.coin_exception import BinanceAPIException, BinanceRequestException

if six.PY2:
    from urllib import urlencode
elif six.PY3:
    from urllib.parse import urlencode


class BinanceTradeApi(object):

    API_URL = 'https://api.binance.com/api'
    PUBLIC_API_VERSION = 'v1'
    PRIVATE_API_VERSION = 'v3'

    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

    ORDER_RESP_TYPE_ACK = 'ACK'
    ORDER_RESP_TYPE_RESULT = 'RESULT'
    ORDER_RESP_TYPE_FULL = 'FULL'

    def __init__(self, api_key, api_secret):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()

        # init DNS and SSL cert
        # self.ping()

    def _init_session(self):

        session = requests.session()
        session.headers.update({'Accept': 'application/json',
                                'User-Agent': 'binance/python',
                                'X-MBX-APIKEY': self.API_KEY})
        return session

    def _create_api_uri(self, path, signed=True, version=PUBLIC_API_VERSION):
        v = self.PRIVATE_API_VERSION if signed else version
        return self.API_URL + '/' + v + '/' + path

    def _request_api(self, method, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        uri = self._create_api_uri(path, signed, version)

        return self._request(method, uri, signed, **kwargs)

    def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('get', path, signed, version, **kwargs)

    def _post(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('post', path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('delete', path, signed, version, **kwargs)

    @staticmethod
    def _handle_response(response):
        """
        处理response
        :param response:
        :return:
        """
        if not str(response.status_code).startswith('2'):
            raise BinanceAPIException(response.text)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

    # 这步骤是必要的吗？
    def _order_params(self, data):
        """Convert params to list with signature as last element
        :param data:
        :return:
        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _request(self, method, uri, signed, force_params=False, **kwargs):

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data
        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        if data and (method == 'get' or force_params):
            kwargs['params'] = self._order_params(kwargs['data'])
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _generate_signature(self, data):
        query_string = urlencode(data)
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def ping(self):
        return self._get('ping')

    def get_server_time(self):
        """Test connectivity to the Rest API and get the current server time.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#check-server-time
        :returns: Current server time
        .. code-block:: python
            {
                "serverTime": 1499827319559
            }
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('time')

    def get_all_tickers(self):
        """Latest price for all symbols.
        https://www.binance.com/restapipub.html#symbols-price-ticker
        :returns: List of market tickers
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('ticker/allPrices')

    def get_orderbook_tickers(self):
        """Best price/qty on the order book for all symbols.
        https://www.binance.com/restapipub.html#symbols-order-book-ticker
        :returns: List of order book market entries
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('ticker/allBookTickers')

    def get_order_book(self, **params):
        """Get the Order Book for the market
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book
        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 100
        :type limit: int
        :returns: API response
        .. code-block:: python
            {
                "lastUpdateId": 1027024,
                "bids": [
                    [
                        "4.00000000",     # PRICE
                        "431.00000000",   # QTY
                        []                # Can be ignored
                    ]
                ],
                "asks": [
                    [
                        "4.00000200",
                        "12.00000000",
                        []
                    ]
                ]
            }
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('depth', data=params)

    def create_order(self, **params):
        """Send in a new order
        Any order with an icebergQty MUST have timeInForce set to GTC.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade
        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param type: required
        :type type: enum
        :param timeInForce: required if limit order
        :type timeInForce: enum
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :returns: API response
        Response ACK:
        .. code-block:: python
            {
                "symbol":"LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1" # Will be newClientOrderId
                "transactTime": 1499827319559
            }
        Response RESULT:
        .. code-block:: python
            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL"
            }
        Response FULL:
        .. code-block:: python
            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL",
                "fills": [
                    {
                        "price": "4000.00000000",
                        "qty": "1.00000000",
                        "commission": "4.00000000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3999.00000000",
                        "qty": "5.00000000",
                        "commission": "19.99500000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3998.00000000",
                        "qty": "2.00000000",
                        "commission": "7.99600000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3997.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99700000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3995.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99500000",
                        "commissionAsset": "USDT"
                    }
                ]
            }
        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException
        """
        return self._post('order', True, data=params)

    def order_market(self, **params):
        """Send in a new market order
        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :returns: API response
        See order endpoint for full response options
        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException
        """
        params.update({
            'type': self.ORDER_TYPE_MARKET
        })
        return self.create_order(**params)

    def order_market_buy(self, symbol, quantity, newClientOrderId=None, newOrderRespType=None):
        """Send in a new market buy order
        默认get ack就好了
        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :returns: API response
        See order endpoint for full response options
        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException
        """
        params = {
            'side': self.SIDE_BUY,
            'symbol': symbol,
            'quantity': quantity
        }
        if newClientOrderId is not None:
            params['newClientOrderId'] = newClientOrderId
        if newOrderRespType is not None:
            params['newOrderRespType'] = newOrderRespType
        else:
            params['newOrderRespType'] = self.ORDER_RESP_TYPE_ACK
        return self.order_market(**params)

    def order_market_sell(self, symbol, quantity, newClientOrderId=None, newOrderRespType=None):
        """Send in a new market sell order
        默认get ack就好了
        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :returns: API response
        See order endpoint for full response options
        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException
        """
        params = {
            'side': self.SIDE_SELL,
            'symbol': symbol,
            'quantity': quantity
        }
        if newClientOrderId is not None:
            params['newClientOrderId'] = newClientOrderId
        if newOrderRespType is not None:
            params['newOrderRespType'] = newOrderRespType
        else:
            params['newOrderRespType'] = self.ORDER_RESP_TYPE_ACK
        return self.order_market(**params)

    def create_test_order(self, **params):
        """Test new order creation and signature/recvWindow long. Creates and validates a new order but does not send it into the matching engine.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-new-order-trade
        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param type: required
        :type type: enum
        :param timeInForce: required if limit order
        :type timeInForce: enum
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :param recvWindow: The number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            {}
        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException
        """
        return self._post('order/test', True, data=params)

    def get_order(self, **params):
        """Check an order's status. Either orderId or origClientOrderId must be sent.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-order-user_data
        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param origClientOrderId: optional
        :type origClientOrderId: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            {
                "symbol": "LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1",
                "price": "0.1",
                "origQty": "1.0",
                "executedQty": "0.0",
                "status": "NEW",
                "timeInForce": "GTC",
                "type": "LIMIT",
                "side": "BUY",
                "stopPrice": "0.0",
                "icebergQty": "0.0",
                "time": 1499827319559
            }
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('order', True, data=params)

    def get_all_orders(self, **params):
        """Get all account orders; active, canceled, or filled.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#all-orders-user_data
        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param limit: Default 500; max 500.
        :type limit: int
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('allOrders', True, data=params)

    def cancel_order(self, symbol, orderId):
        """Cancel an active order. Either orderId or origClientOrderId must be sent.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-order-trade
        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :returns: API response
        .. code-block:: python
            {
                "symbol": "LTCBTC",
                "origClientOrderId": "myOrder1",
                "orderId": 1,
                "clientOrderId": "cancelMyOrder1"
            }
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._delete('order', True, data=dict(symbol=symbol, orderId=orderId))

    def get_open_orders(self, **params):
        """Get all open orders on a symbol.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-open-orders-user_data
        :param symbol: required
        :type symbol: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('openOrders', True, data=params)

    def get_account(self, **params):
        """Get current account information.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        .. code-block:: python
            {
                "makerCommission": 15,
                "takerCommission": 15,
                "buyerCommission": 0,
                "sellerCommission": 0,
                "canTrade": true,
                "canWithdraw": true,
                "canDeposit": true,
                "balances": [
                    {
                        "asset": "BTC",
                        "free": "4723846.89208129",
                        "locked": "0.00000000"
                    },
                    {
                        "asset": "LTC",
                        "free": "4763368.68006011",
                        "locked": "0.00000000"
                    }
                ]
            }
        :raises: BinanceResponseException, BinanceAPIException
        """
        return self._get('account', True, data=params)
