# -*- coding=utf-8 -*-
"""
测试币安和交易相关API
"""
from decimal import Decimal
from coin.lib.api.binance import BinanceTradeApi


trade_api = BinanceTradeApi()


def test_account():
    print trade_api.get_account()


def test_place_order_buy():
    return trade_api.order_market_buy(symbol='IOSTBTC', quantity=Decimal('10'), newOrderRespType='FULL')


def test_query_order(test_order_id):
    return trade_api.get_order(symbol='IOSTBTC', orderId=test_order_id)


def test_place_order_sell():
    return trade_api.order_market_sell(symbol='IOSTBTC', quantity=Decimal('10'))


def test_cancel_order(test_order_id):
    return trade_api.cancel_order(symbol='IOSTBTC', orderId=test_order_id)


if __name__ == '__main__':
    # test_account()
    # print test_place_order_buy()
    order_id = 4757205
    print test_query_order(order_id)
    # res = test_place_order_sell()
    # print res
    # order_id = res['orderId']
    # print test_query_order(order_id)
    # print test_cancel_order(order_id)
