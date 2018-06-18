# -*- coding=utf-8 -*-
from datetime import datetime
from coin.model.trade_info import CombinationTradeInfoModel
from coin.model.base import clear_dbsession
from coin.lib.utils import OrderState


class SqlTraderInfo(object):
    """
    存储在sql中
    """

    @staticmethod
    def add_new_trade(combination, trade_pair_id, market, order_id, symbol, trade_side, trade_target,
                      amount, price, depth_str, depth_time, create_time):
        """
        添加新的交易
        :param order_id:
        :type order_id: int或者None
        :param trade_pair_id:
        :param market:
        :param symbol:
        :param trade_side:
        :param trade_target:
        :param amount:
        :param price:
        :param depth_str: json序列化之后的深度信息
        :return:
        """
        depth_time = datetime.utcfromtimestamp(1.0 * depth_time / 1000)  # depth time 都是毫秒时间戳
        CombinationTradeInfoModel(combination=combination, trade_pair_id=trade_pair_id, market=market,
                                  order_id=order_id, symbol=symbol, trade_side=trade_side, trade_target=trade_target,
                                  query_amount=amount, query_price=price, state=OrderState.New, depth=depth_str,
                                  depth_time=depth_time, create_time=create_time).add()

    @staticmethod
    def add_exception_trade(combination, trade_pair_id, market, order_id, symbol, trade_side, trade_target,
                            amount, price, depth_str, depth_time, exception_message, create_time):
        """
        添加异常交易
        :param order_id:
        :param trade_pair_id:
        :param market:
        :param symbol:
        :param trade_side:
        :param trade_target:
        :param amount:
        :param price:
        :param depth_str: json序列化之后的深度信息
        :param exception_message:
        :return:
        """
        depth_time = datetime.utcfromtimestamp(1.0 * depth_time / 1000)  # depth time 都是毫秒时间戳
        CombinationTradeInfoModel(combination=combination, trade_pair_id=trade_pair_id, market=market,
                                  order_id=order_id, symbol=symbol, trade_side=trade_side, trade_target=trade_target,
                                  query_amount=amount, query_price=price, state=OrderState.Exception, depth=depth_str,
                                  depth_time=depth_time, create_time=create_time,
                                  exception_message=exception_message).add()

    @staticmethod
    def clear_session():
        clear_dbsession()
