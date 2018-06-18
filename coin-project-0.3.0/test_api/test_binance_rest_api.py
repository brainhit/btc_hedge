# -*- coding=utf-8 -*-
from coin.lib.api.binance import BinanceTradeApi


trade_api = BinanceTradeApi()


def test_ping():
    print trade_api.ping()


def test_server_time():
    return trade_api.get_server_time()


def test_get_order_book():
    print trade_api.get_order_book(symbol='ETHBTC', limit=20)


if __name__ == '__main__':
    # test_ping()
    # test_server_time()
    test_get_order_book()
    # 测试时间
    # import time
    # start = time.time()
    # res = test_server_time()['serverTime']
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_server_time()['serverTime']
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_server_time()['serverTime']
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_server_time()['serverTime']
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_server_time()['serverTime']
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
