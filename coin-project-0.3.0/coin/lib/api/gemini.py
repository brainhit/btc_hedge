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
from coin.lib.config import TIMEOUT
from coin.lib.utils import OrderType, RequestMethods
from coin.lib.coin_exception import ApiRequestError, ParamsError


class GeminiTradeApi(object):

    REQUEST_SEND_ERROR = 'REQUEST_SEND_ERROR'
    REQUEST_STATUS_ERROR = 'REQUEST_STATUS_ERROR'
    BASE_URL = 'https://api.gemini.com'

    # 交易相关api
    def __init__(self, api_key, api_secret):
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
        host_url = self.TRADE_URL

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

        host_url = self.TRADE_URL
        host_name = urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.create_signature(params_to_sign, method, host_name,
                                                            request_path, self.secret_key)
        url = host_url + request_path + '?' + urllib.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    def get_ticker(self, symbol):
        """
        拿取ticker
        :param symbol: like btcusd
        :return:
        {
            "ask": "977.59",
            "bid": "977.35",
            "last": "977.65",
            "volume": {
                "BTC": "2210.505328803",
                "USD": "2135477.463379586263",
                "timestamp": 1483018200000
            }
        }
        """
        path = '/v1/pubticker/{}'.format(symbol)
        return self.api_key_get(dict(), path, need_signature=False)

    def get_depth(self, symbol, limit_bids=10, limit_asks=10):
        """
        获取市场深度
        :param symbol:
        :param limit_bids:
        :param limit_asks:
        :return:
        {
          "bids": [{
                    "amount": "1",
                    "price": "9708.84",
                    "timestamp": "1519754039"
                   }],
          "asks": [{
                    "amount": "1",
                    "price": "9698.76",
                    "timestamp": "1519754039"
                   }]
        }
        """
        path = '/v1/book/{}'.format(symbol)
        return self.api_key_get(dict(limit_bids=limit_bids, limit_asks=limit_asks),
                                path, need_signature=False)

    def get_trade_history(self, symbol, since=None, limit_trades=50, include_breaks=False):
        """
        获取交易历史
        :param symbol:
        :param since:
        :param limit_trades:
        :param include_breaks:
        :return:
        [
          {
            "timestamp": 1420088400,
            "timestampms": 1420088400122,
            "tid": 155814,
            "price": "822.12",
            "amount": "12.10",
            "exchange": "gemini",
            "type": "buy"
          },
          ...
        ]
        """
        path = '/v1/trades/{}'.format(symbol)
        params = dict(include_breaks=include_breaks, limit_trades=limit_trades)
        if since is not None:
            params['since'] = since
        return self.api_key_get(params, path, need_signature=False)

    def get_current_auction(self, symbol):
        """

        :param symbol:
        :return:
        """
        path = '/v1/auction/{}'.format(symbol)
        return self.api_key_get(dict(), path, need_signature=False)
