# -*- coding=utf-8 -*-
import base64
from Crypto.Cipher import AES
from copy import deepcopy
from decimal import Decimal
from coin.lib.config import low_greedy_coefficient, high_greedy_coefficient, AES_KEY
import os


class Status(object):
    Start = 'Start'
    Active = 'Active'
    End = 'End'


class OrderType(object):

    BuyMarket = 'buy-market'
    SellMarket = 'sell-market'
    BuyLimit = 'buy-limit'
    SellLimit = 'sell-limit'


class Market(object):
    BINANCE = 'BINANCE'
    HUOBI = 'HUOBI'
    OKEX = 'OKEX'
    ZB = 'ZB'


key_prefix = 'COIN:PRICE'
bigcoin_set = {'btc', 'eth'}
ip = os.popen("ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | "
              "grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'").readlines()[0].split('\n')[0]


class OrderState(object):

    New = 'New'
    Filled = 'Filled'
    Exception = 'Exception'
    NotFilled = 'NotFilled'


class TradeTarget(object):

    Hedge = 'Hedge'
    ReBalance = 'ReBalance'
    SmallCoinAdjust = 'SmallCoinAdjust'


class TradeSide(object):

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'


class RequestMethods(object):

    GET = 'GET'
    POST = 'POST'


def get_trade_amount(amount):
    """
    获取小币交易数量
    :param amount:
    :type amount: Decimal
    :return:
    """
    if amount < 100000:
        return amount * low_greedy_coefficient
    else:
        return amount * high_greedy_coefficient


def get_redis_key(market, coin1, coin2):
    """
    获取在redis中的key，大币只考虑有BTC和ETH，而且不考虑大币之间互换
    :param market: 市场
    :param coin1: coin1 name str
    :param coin2: coin2 name str
    :return: key str
    """
    # key采用大币在后
    if coin1.lower() in bigcoin_set:
        return '{}:{}:{}-{}'.format(key_prefix, market, coin2, coin1)
    else:
        return '{}:{}:{}-{}'.format(key_prefix, market, coin1, coin2)


def analysis_redis_key(key):
    """
    分解redis key，返回中大币在前
    :param key:
    :return: market, coin1, coin2
    """
    key_part = key.rsplit(':', 2)
    coin1, coin2 = key_part[-1].split('-')
    market = key_part[-2]
    return market, coin1, coin2


def aes_encrypt(data):
    """
    加密数据
    :param data:
    :return:
    """
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    cipher = AES.new(AES_KEY)
    encrypted = cipher.encrypt(pad(data))  # aes加密
    result = base64.b64encode(encrypted)  # base64 encode
    return result


def aes_decrypt(data):
    """
    解密数据
    :param data:
    :return:
    """
    unpad = lambda s: s[0:-ord(s[-1])]
    cipher = AES.new(AES_KEY)
    result2 = base64.b64decode(data)
    decrypted = unpad(cipher.decrypt(result2))
    return decrypted
