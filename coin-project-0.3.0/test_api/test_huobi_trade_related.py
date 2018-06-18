# -*- coding=utf-8 -*-
"""
测试huobi和交易相关的API
"""
import time
from coin.lib.api.huobi import HuoBiTradeApi, OrderType, OrderState


trade_api = HuoBiTradeApi()


def test_account():
    print trade_api.account_info()


def test_balance():
    print trade_api.get_balance()


def test_huobi_point():
    huobi_point = trade_api.get_huobi_point()
    print huobi_point, type(huobi_point)


def test_place_buy_order():
    return trade_api.place_order(symbol='iostbtc', order_type=OrderType.BuyMarket, amount='0.0001')


def test_place_sell_order():
    return trade_api.place_order(symbol='iostbtc', order_type=OrderType.SellMarket, amount='20')


def test_query_order(test_order_id):
    print trade_api.query_order(test_order_id)


def test_cancel_order(test_order_id):
    trade_api.cancel_order(test_order_id)


def test_batch_query():
    print trade_api.batch_query_orders('iostbtc', OrderState.FILLED, from_order_id=2169736542)


if __name__ == '__main__':
    # test_account()
    # test_balance()
    test_huobi_point()
    # order_id = test_place_buy_order()
    # print order_id
    # test_query_order(order_id)
    # order_id = test_place_sell_order()
    # print order_id
    # test_query_order(order_id)
    # order_id = 2169962795
    # test_cancel_order(order_id)
    # test_batch_query()
