# -*- coding=utf-8 -*-
import hashlib
import requests
from coin.lib.coin_exception import OKExAPIException, OKExRequestException


class OKExTradeApi(object):

    class OrderType(object):
        BuyMarket = 'buy_market'
        SellMarket = 'sell_market'
        BuyLimit = 'buy'
        SellLimit = 'sell'

    def __init__(self, api_key, api_secret):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()
        self.base_url = 'https://www.okex.com/api/v1'

    def _init_session(self):

        session = requests.session()
        # 请求头信息中contentType需要统一设置为：application/x-www-form-urlencoded
        session.headers.update({
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        })
        return session

    def _create_api_uri(self, path):
        return self.base_url + '/' + path

    def _request_api(self, method, path, signed=False, **kwargs):
        uri = self._create_api_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _get(self, path, signed=False, **kwargs):
        return self._request_api('get', path, signed, **kwargs)

    def _post(self, path, signed=False, **kwargs):
        return self._request_api('post', path, signed, **kwargs)

    def _delete(self, path, signed=False, **kwargs):
        return self._request_api('delete', path, signed, **kwargs)

    @staticmethod
    def _handle_response(response):
        """
        处理response
        :param response:
        :return:
        """
        if not str(response.status_code).startswith('2'):
            raise OKExAPIException(response.text)
        try:
            res = response.json()
            if ('result' in res and res['result'] is False) or 'error_code' in res:
                raise ValueError
            return res
        except ValueError:
            raise OKExRequestException('Invalid Response: %s' % response.text)

    def _request(self, method, uri, signed, **kwargs):

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data
        if signed:
            # generate signature
            kwargs['data']['sign'] = self._generate_signature(kwargs['data'])
        if method == 'get':
            kwargs['params'] = kwargs['data']
            del kwargs['data']

        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _generate_signature(self, params):
        """
        To build MD5 sign for user's parameters.
        :param params: User's parameters usually in the format of a dict
        :return: Signed string encrypted by MD5
        """
        sign = ''
        if hasattr(params, 'items'):
            for key in sorted(params.keys()):
                sign += key + '=' + str(params[key]) + '&'
            data = sign + 'secret_key=' + self.API_SECRET
        else:
            raise TypeError('{0} should has attributes of "items"'.format(params))
        return hashlib.md5(data.encode('utf8')).hexdigest().upper()

    def get_market_depth(self, symbol, size=10):
        """
        获取市场深度信息
        :param symbol:
        :param size:
        :return:
        {
            "asks": [
                [792, 5],
                [789.68, 0.018],
                [788.99, 0.042],
                [788.43, 0.036],
                [787.27, 0.02]
            ],
            "bids": [
                [787.1, 0.35],
                [787, 12.071],
                [786.5, 0.014],
                [786.2, 0.38],
                [786, 3.217],
                [785.3, 5.322],
                [785.04, 5.04]
            ]
        }
        """
        return self._get(path='depth.do', signed=False, data=dict(symbol=symbol, size=size))

    def get_account(self):
        """
        获取货币信息
        :return:
        {
            "free": {
                "btc": "0",
                "usd": "0",
                "ltc": "0",
                "eth": "0"
            },
            "freezed": {
                "btc": "0",
                "usd": "0",
                "ltc": "0",
                "eth": "0"
            }
        }
        """
        return self._post(path='userinfo.do', signed=True, data=dict(api_key=self.API_KEY))['info']['funds']

    def place_order(self, symbol, order_type, price, amount):
        """
        下订单
        symbol	String	是	币对如ltc_btc
        type	String	是	买卖类型：限价单(buy/sell) 市价单(buy_market/sell_market)
        price	Double	否	下单价格 市价卖单不传price
        amount	Double	否	交易数量 市价买单不传amount
        :param symbol:
        :param order_type:
        :param price:
        :param amount:
        :return: order_id
        """
        data = dict(symbol=symbol, type=order_type, api_key=self.API_KEY)
        if price is not None:
            data['price'] = price
        if amount is not None:
            data['amount'] = amount
        return self._post(path='trade.do', signed=True, data=data)['order_id']

    def market_buy(self, symbol, price):
        """
        市价买
        :param symbol:
        :param price: 要买多少价格的东西
        :return: order_id
        """
        return self.place_order(symbol=symbol, order_type=self.OrderType.BuyMarket, price=price, amount=None)

    def market_sell(self, symbol, amount):
        """
        市价卖
        :param symbol:
        :param amount: 卖多少数量
        :return: order_id
        """
        return self.place_order(symbol=symbol, order_type=self.OrderType.SellMarket, price=None, amount=amount)

    def cancel_order(self, symbol, order_id):
        """
        取消单个订单
        :param symbol:
        :param order_id:
        :return: True/False
        """
        return self._post(path='cancel_order.do', signed=True,
                          data=dict(api_key=self.API_KEY, symbol=symbol, order_id=order_id))

    def get_order(self, symbol, order_id):
        """
        查询订单信息
        :param symbol:
        :param order_id:
        :return:
        "orders":[
            {
                "order_id":15088,
                "status":0,  -1:已撤销  0:未成交  1:部分成交  2:完全成交 3:撤单处理中
                "symbol":"btc_usd",
                "type":"sell",
                "price":811,
                "amount":1.39901357,
                "deal_amount":1,
                "avg_price":811
            } ,
        ]
        """
        return self._post(path='order_info.do', signed=True,
                          data=dict(api_key=self.API_KEY, symbol=symbol, order_id=order_id))['orders']
