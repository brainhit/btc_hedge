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


class ZBTradeApi(object):

    TRADE_URL = 'http://api.zb.com'
    REQUEST_SEND_ERROR = 'REQUEST_SEND_ERROR'
    REQUEST_STATUS_ERROR = 'REQUEST_STATUS_ERROR'

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

    def get_markets(self):
        """
        获取ZB最新市场配置数据
        :return:
        {
            "btc_usdt": {
                "amountScale": 4,
                "priceScale": 2
            },
            "ltc_usdt": {
                "amountScale": 3,
                "priceScale": 2
            }
            ...
        }
        """
        path = '/data/v1/markets'
        return self.api_key_get(dict(), path, need_signature=False)

    def get_ticker(self, symbol):
        """
        获取最新市场行情数据
        :param symbol: like btc_usdt
        :return:
        {
            "ticker": {
                "vol": "40.463",
                "last": "0.899999",
                "sell": "0.5",
                "buy": "0.225",
                "high": "0.899999",
                "low": "0.081"
            },
            "date": "1507875747359"
        }
        """
        path = '/data/v1/ticker'
        return self.api_key_get(dict(market=symbol), path, need_signature=False)

    def get_depth(self, symbol, size=10):
        """
        获取市场深度
        :param symbol:
        :param size:
        :return:
        {
            "asks": [
                [
                    83.28,
                    11.8
                ]...
            ],
            "bids": [
                [
                    81.91,
                    3.65
                ]...
            ],
            "timestamp" : 时间戳
        }
        """
        path = '/data/v1/depth'
        return self.api_key_get(dict(market=symbol, size=size), path, need_signature=False)
