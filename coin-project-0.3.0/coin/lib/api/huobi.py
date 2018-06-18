# -*- coding=utf-8 -*-
from datetime import datetime
from decimal import Decimal
import base64
import hashlib
import hmac
import json
import requests
import urllib
from urlparse import urlparse
from coin.lib.config import TIMEOUT, TRADE_URL
from coin.lib.utils import OrderType
from coin.lib.coin_exception import ApiRequestError, ParamsError


class RequestMethods(object):

    GET = 'GET'
    POST = 'POST'


class OrderState(object):

    PRE_SUBMITTED = 'pre-submitted'  # 准备提交
    SUBMITTING = 'submitting'  # 正在提交
    SUBMITTED = 'submitted'  # 已提交,
    PARTIAL_FILLED = 'partial-filled'  # 部分成交
    PARTIAL_CANCELED = 'partial-canceled'  # 部分成交撤销,
    FILLED = 'filled'  # 完全成交,
    CANCELED = 'canceled'  # 已撤销


class HuoBiTradeApi(object):

    REQUEST_SEND_ERROR = 'REQUEST_SEND_ERROR'
    REQUEST_STATUS_ERROR = 'REQUEST_STATUS_ERROR'

    # 交易相关api
    def __init__(self, api_key, api_secret, account_id, huobipoint_account_id=None):
        self.account_id = account_id
        self.huobipoint_account_id = huobipoint_account_id
        self.api_key = api_key
        self.secret_key = api_secret
        self.session = requests.Session()

    def http_get_request(self, url, params, add_to_headers=None):
        """
        发送get请求
        :param url:
        :param params:
        :param add_to_headers:
        :return:
        """
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = urllib.urlencode(params)
        try:
            response = self.session.get(url, params=postdata, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "fail", 'err-code': self.REQUEST_STATUS_ERROR, 'err-msg': response.text}
        except Exception as e:
            return {"status": "fail", 'err-code': self.REQUEST_SEND_ERROR,  "err-msg": e}

    def http_post_request(self, url, params, add_to_headers=None):
        """
        发送post请求
        :param url:
        :param params:
        :param add_to_headers:
        :return:
        """
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
            "User-Agent": "Chrome/39.0.2171.71",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = json.dumps(params)
        try:
            response = self.session.post(url, postdata, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "fail", 'err-code': self.REQUEST_STATUS_ERROR, 'err-msg': response.text}
        except Exception as e:
            return {"status": "fail", 'err-code': self.REQUEST_SEND_ERROR,  "err-msg": e}

    def api_key_get(self, params, request_path, need_signature=True):
        host_url = TRADE_URL

        if need_signature:
            method = RequestMethods.GET
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            params.update({'AccessKeyId': self.api_key,
                           'SignatureMethod': 'HmacSHA256',
                           'SignatureVersion': '2',
                           'Timestamp': timestamp})
            host_name = urlparse(host_url).hostname
            host_name = host_name.lower()
            params['Signature'] = self.create_signature(params, method, host_name, request_path, self.secret_key)

        url = host_url + request_path
        return self.http_get_request(url, params)

    def api_key_post(self, params, request_path):
        method = 'POST'
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.api_key,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = TRADE_URL
        host_name = urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.create_signature(params_to_sign, method, host_name,
                                                            request_path, self.secret_key)
        url = host_url + request_path + '?' + urllib.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    @staticmethod
    def create_signature(params, method, host_url, request_path, secret_key):
        sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')
        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature

    def supported_symbols(self):
        """
        支持的交易对
        :return:
        """
        path = '/v1/common/symbols'
        symbols_result = self.api_key_get(dict(), path, need_signature=False)
        if symbols_result['status'] == 'ok':
            return symbols_result['data']
        else:
            print symbols_result['msg']

    def get_server_time(self):
        """
        获取服务器时间
        :return:
        """
        path = '/v1/common/timestamp'
        symbols_result = self.api_key_get(dict(), path, need_signature=False)
        if symbols_result['status'] == 'ok':
            return symbols_result['data']
        else:
            print symbols_result['msg']

    def account_info(self):
        """
        账号信息
        :return:
        [
        {
          "id": 100009,
          "type": "spot",
          "state": "working",
          "user-id": 1000
        }
      ]
        """
        path = '/v1/account/accounts'
        account_result = self.api_key_get(dict(), path)
        if account_result['status'] == 'ok':
            return account_result['data']
        else:
            print account_result
            raise ApiRequestError('Error Get Account, Error Code {}, Error Message {}'.
                                  format(account_result['err-code'], account_result['err-msg']))

    def get_balance(self):
        """
        获取账号币种余额
        :return:
        {
        "id": 100009,
        "type": "spot",
        "state": "working",
        "list": [
          {
            "currency": "usdt",
            "type": "trade",
            "balance": "500009195917.4362872650"
          },
          {
            "currency": "usdt",
            "type": "frozen",
            "balance": "328048.1199920000"
          },
         {
            "currency": "etc",
            "type": "trade",
            "balance": "499999894616.1302471000"
          },
          {
            "currency": "etc",
            "type": "frozen",
            "balance": "9786.6783000000"
          }
         {
            "currency": "eth",
            "type": "trade",
            "balance": "499999894616.1302471000"
          },
          {
            "currency": "eth”,
            "type": "frozen",
            "balance": "9786.6783000000"
          }
        ],
      }
        """
        path = '/v1/account/accounts/{account_id}/balance'.format(account_id=self.account_id)
        balance_result = self.api_key_get(dict(), path)
        if balance_result['status'] == 'ok':
            return balance_result['data']
        else:
            raise ApiRequestError('Error Get Balance, Error Code {}, Error Message {}'.
                                  format(balance_result['err-code'], balance_result['err-msg']))

    def get_huobi_point(self):
        """
        获取火币点数
        :return: Decimal
        """
        if not self.huobipoint_account_id:  # 没有火币点卡账号
            return Decimal('0')
        path = '/v1/account/accounts/{account_id}/balance'.format(account_id=self.huobipoint_account_id)
        balance_result = self.api_key_get(dict(), path)
        if balance_result['status'] == 'ok':
            huobi_point_data = balance_result['data']['list']
            res = Decimal('0')
            for item in huobi_point_data:
                if item['currency'] == 'hbpoint':
                    res += Decimal(item['balance'])
            return res
        else:
            raise ApiRequestError('Error Get Balance, Error Code {}, Error Message {}'.
                                  format(balance_result['err-code'], balance_result['err-msg']))

    def get_market_depth(self, symbol, depth='step0'):
        """
        获取交易深度信息
        :param symbol:
        :param depth:
        :return: 1489472598812（消息生成时间）, tick
        tick格式如下
        "tick": {
            "id": 消息id,
            "ts": 消息生成时间，单位：毫秒,
            "bids": 买盘,[price(成交价), amount(成交量)], 按price降序,
            "asks": 卖盘,[price(成交价), amount(成交量)], 按price升序
          }
        """
        path = '/market/depth?symbol={}&type={}'.format(symbol, depth)
        balance_result = self.api_key_get(dict(), path, need_signature=False)
        if balance_result['status'] == 'ok':
            return balance_result['ts'], balance_result['tick']
        else:
            print balance_result['err-code'], balance_result['err-msg']

    def place_order(self, symbol, order_type, amount, price=None):
        """
        下订单，暂时不使用借贷资产交易
        对于iostbtc, huobi的市场价买里面填的是比特币的数量，市场价卖填的是iost的数量
        :param symbol:
        :param order_type:
        :param amount: 限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币 string类型
        :param price: 下单价格，市价单不传该参数
        :return: order_id
        """
        path = '/v1/order/orders/place'
        params = {
            'account-id': self.account_id,
            'amount': amount,
            'source': 'api',
            'symbol': symbol,
            'type': order_type
        }
        if order_type == OrderType.BuyLimit or order_type == OrderType.SellLimit:
            if price is None:
                raise ParamsError('Missing price in limit order')
            params['price'] = price
        order_result = self.api_key_post(params=params, request_path=path)
        if order_result['status'] == 'ok':
            return order_result['data']
        else:
            raise ApiRequestError('Error Place Order, Error Code {}, Error Message {}'.
                                  format(order_result['err-code'], order_result['err-msg']))

    def query_order(self, order_id):
        """
        获取订单信息
        :param order_id:
        :return: order info
        """
        path = '/v1/order/orders/{order_id}'.format(order_id=order_id)
        order_info = self.api_key_get(dict(), path)
        if order_info['status'] == 'ok':
            return order_info['data']
        else:
            raise ApiRequestError('Error Query Order, Error Code {}, Error Message {}'.
                                  format(order_info['err-code'], order_info['err-msg']))

    def cancel_order(self, order_id):
        """
        申请取消订单
        注意，返回OK表示撤单请求成功。订单是否撤销成功请调用订单查询接口查询该订单状态
        :param order_id:
        :return: 申请提交不成功则抛出异常
        """
        path = '/v1/order/orders/{order_id}/submitcancel'.format(order_id=order_id)
        cancel_result = self.api_key_post(params={}, request_path=path)
        if cancel_result['status'] == 'ok':
            return cancel_result['data']
        else:
            raise ApiRequestError('Error Cancel Order, Error Code {}, Error Message {}'.
                                  format(cancel_result['err-code'], cancel_result['err-msg']))

    def batch_cancel_order(self, order_id_list):
        """
        批量申请取消订单
        注意，返回OK表示撤单请求成功。订单是否撤销成功请调用订单查询接口查询该订单状态
        :param order_id_list:
        :return:
        "success": [
          "1",
          "3"
        ],
        "failed": [
          {
            "err-msg": "记录无效",
            "order-id": "2",
            "err-code": "base-record-invalid"
          }
        ]
        """
        path = '/v1/order/orders/batchcancel'
        params = {'order-ids': order_id_list}
        cancel_result = self.api_key_post(params=params, request_path=path)
        if cancel_result['status'] == 'ok':
            return cancel_result['data']
        else:
            raise ApiRequestError('Error Batch Cancel Order, Error Code {}, Error Message {}'.
                                  format(cancel_result['err-code'], cancel_result['err-msg']))

    def batch_query_orders(self, symbol, states, order_type=None, start_date=None, end_date=None,
                           from_order_id=None, direct=None, size=None):
        """
        查询当前委托、历史委托，先只支持
        :param symbol: 交易对
        :param states: str 查询的订单状态组合，使用','分割
        :param order_type: 查询的订单类型组合，使用','分割
        :param start_date: 查询开始日期, 日期格式yyyy-mm-dd
        :param end_date: 查询结束日期, 日期格式yyyy-mm-dd
        :param from_order_id: 查询起始 ID
        :param direct: 查询方向
        :param size: 查询记录大小
        [
            {
              "id": 59378,
              "symbol": "ethusdt",
              "account-id": 100009,
              "amount": "10.1000000000",
              "price": "100.1000000000",
              "created-at": 1494901162595,
              "type": "buy-limit",
              "field-amount": "10.1000000000",
              "field-cash-amount": "1011.0100000000",
              "field-fees": "0.0202000000",
              "finished-at": 1494901400468,
              "user-id": 1000,
              "source": "api",
              "state": "filled",
              "canceled-at": 0,
              "exchange": "huobi",
              "batch": ""
            }
        ]
        :return:
        """
        path = '/v1/order/orders'
        params = {
            'symbol': symbol,
            'states': states
        }
        if order_type:
            params['types'] = order_type
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if from_order_id:
            params['from'] = from_order_id
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        query_result = self.api_key_get(params=params, request_path=path)
        if query_result['status'] == 'ok':
            return query_result['data']
        else:
            raise ApiRequestError('Error Batch Query Order, Error Code {}, Error Message {}'.
                                  format(query_result['err-code'], query_result['err-msg']))
