# -*- coding=utf-8 -*-
"""
修复火币卖时候的数量
"""
from datetime import datetime
from decimal import Decimal
import time
import traceback
from sqlalchemy import and_
from coin.lib.utils import OrderState, Market, TradeSide
from coin.model.trade_info import CombinationTradeInfoModel
from coin.lib.combination.huobi_binance_trade_task import HuobiBinanceCombinationTask
from coin.model.base import get_dbsession


def run():
    obj_dict = dict()
    session = get_dbsession()
    try:
        order_list = session.query(CombinationTradeInfoModel) \
            .filter(and_(CombinationTradeInfoModel.state == OrderState.Filled,
                         CombinationTradeInfoModel.market == Market.HUOBI,
                         CombinationTradeInfoModel.trade_side == TradeSide.SIDE_SELL)) \
            .all()
        for order_data in order_list:
            # 这种情况不应该发生
            if order_data.order_id is None:
                print("{}|InvalidOrder|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                        order_data.trade_pair_id, order_data.combination,
                                                        order_data.market))
                continue
            if order_data.combination not in obj_dict:
                try:
                    _obj = HuobiBinanceCombinationTask(rds=None, combination=order_data.combination)
                    obj_dict[order_data.combination] = _obj
                except:
                    obj_dict[order_data.combination] = None
            combination_obj = obj_dict.get(order_data.combination)
            if combination_obj is None:
                print("{}|CombinationNotFound|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                               order_data.trade_pair_id, order_data.combination,
                                                               order_data.market))
                continue
            huobi_order_info = combination_obj.huobi_trade_api.query_order(order_data.order_id)
            # 先只管订单完成了的
            if huobi_order_info['state'] == 'filled':
                order_data.filled_amount = Decimal(huobi_order_info['field-cash-amount'])
                print("{}|ChangeFilledAmount|{}|{}|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                              order_data.trade_pair_id, order_data.combination,
                                                              order_data.market, order_data.trade_side,
                                                                    order_data.filled_amount))
                session.commit()
            # 1s最多一次操作
            time.sleep(1)
    except Exception as e:
        print("{}|TaskError|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                          e.message, traceback.format_exc()))
        # 重开对象
        session.rollback()
    print("{}|WaitForNextTurn".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
    # 休息1分钟
    time.sleep(60)


if __name__ == '__main__':
    run()

