# -*- coding=utf-8 -*-
import time
from coin.lib.api.huobi import HuoBiTradeApi


trade_api = HuoBiTradeApi()


def test_supported_symbols():
    print trade_api.supported_symbols()
    # return trade_api.supported_symbols()


def test_get_accounts():
    print trade_api.account_info()
    # return trade_api.account_info()


def test_get_balance():
    print trade_api.get_balance()
    # return trade_api.get_balance()


def test_get_market_depth():
    print trade_api.get_market_depth('chatbtc')
    # import time
    # print int(time.time() * 1000)
    # return trade_api.get_market_depth('chatbtc')


def test_get_server_time():
    return trade_api.get_server_time()


if __name__ == '__main__':
    # start = time.time()
    # test_supported_symbols()
    # test_get_accounts()
    # test_get_balance()
    test_get_market_depth()
    # end = time.time()
    # print end - start
    # import grequests
    # start = time.time()
    # req = [test_supported_symbols(), test_get_accounts(), test_get_balance(), test_get_market_depth()]
    # res = grequests.map(req)
    # end = time.time()
    # print end - start
    # for item in res:
    #     print item
    # test_supported_symbols()

    # start = time.time()
    # from threading import Thread
    # for _ in xrange(2):
    #     t1 = Thread(target=test_supported_symbols)
    #     t1.start()
    #     # t1.run()
    #     t2 = Thread(target=test_get_accounts)
    #     t2.start()
    #     # t2.run()
    #     t3 = Thread(target=test_get_balance)
    #     t3.start()
    #     # t3.run()
    #     t4 = Thread(target=test_get_market_depth)
    #     t4.start()
    # # t4.run()
    # end = time.time()
    # print end - start

    # import time
    # start = time.time()
    # res = test_get_server_time()
    # print res
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_get_server_time()
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_get_server_time()
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_get_server_time()
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
    # start = time.time()
    # res = test_get_server_time()
    # end = time.time()
    # print int(start*1000), res, int(end*1000)
    # print res-int(start*1000), int(end*1000)-res
