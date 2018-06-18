# -*- coding=utf-8 -*-
"""
检查订单状态
"""
from datetime import datetime
from decimal import Decimal
import time
import traceback
from sqlalchemy import and_
from coin.lib.utils import OrderState, Market, TradeSide, ip
from coin.model.trade_info import CombinationTradeInfoModel
from coin.lib.combination.combination import Combination
from coin.lib.combination.huobi_binance_trade_task import HuobiBinanceCombinationTask
from coin.lib.combination.okex_binance_trade_task import OKExBinanceCombinationTask
from coin.lib.combination.huobi_okex_trade_task import HuobiOKExCombinationTask
from coin.model.base import get_dbsession
from coin.model.exception_info import ExceptionInfoModel


def get_task_object(rds, combination):
    combination_obj = Combination.fetch_by_combination(combination)
    if combination_obj.first_market == Market.HUOBI and combination_obj.second_market == Market.BINANCE:
        task_obj = HuobiBinanceCombinationTask(rds=rds, combination=combination)
    elif combination_obj.first_market == Market.OKEX and combination_obj.second_market == Market.BINANCE:
        task_obj = OKExBinanceCombinationTask(rds=rds, combination=combination)
    elif combination_obj.first_market == Market.HUOBI and combination_obj.second_market == Market.OKEX:
        task_obj = HuobiOKExCombinationTask(rds=rds, combination=combination)
    else:
        raise ValueError('Unsupported combination {}'.format(combination))
    return task_obj


def run():
    obj_dict = dict()
    session = get_dbsession()
    while 1:
        try:
            order_list = session.query(CombinationTradeInfoModel)\
                .filter(and_(CombinationTradeInfoModel.state != OrderState.Filled,
                             CombinationTradeInfoModel.state != OrderState.Exception))\
                .order_by(CombinationTradeInfoModel.create_time.desc()).limit(10)
            session.commit()
            # 移除之前没找到的combination
            for k, v in obj_dict.items():
                if v is None:
                    del obj_dict[k]
            for order_data in order_list:
                # 这种情况不应该发生
                if order_data.order_id is None:
                    print("{}|InvalidOrder|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                            order_data.trade_pair_id, order_data.combination,
                                                            order_data.market))
                    continue
                if order_data.combination not in obj_dict:
                    try:
                        _obj = get_task_object(rds=None, combination=order_data.combination)
                        obj_dict[order_data.combination] = _obj
                    except:
                        obj_dict[order_data.combination] = None
                combination_obj = obj_dict.get(order_data.combination)
                if combination_obj is None:
                    print("{}|CombinationNotFound|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                                   order_data.trade_pair_id, order_data.combination,
                                                                   order_data.market))
                    continue
                if order_data.market == Market.HUOBI:
                    huobi_order_info = combination_obj.huobi_trade_api.query_order(order_data.order_id)
                    # 先只管订单完成了的
                    if huobi_order_info['state'] == 'filled':
                        order_data.state = OrderState.Filled
                        if order_data.trade_side == TradeSide.SIDE_BUY:
                            order_data.filled_amount = Decimal(huobi_order_info['field-amount'])
                        else:
                            order_data.filled_amount = Decimal(huobi_order_info['field-cash-amount'])
                        order_data.filled_fees = Decimal(huobi_order_info['field-fees'])
                        order_data.order_time = datetime.utcfromtimestamp(1.0 * huobi_order_info['created-at'] / 1000)
                        session.commit()
                        print("{}|OrderFilled|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                               order_data.trade_pair_id, order_data.combination,
                                                               order_data.market))
                elif order_data.market == Market.BINANCE:
                    binance_order_info = combination_obj.binance_trade_api.get_order(symbol=order_data.symbol,
                                                                                     orderId=order_data.order_id)
                    if binance_order_info['status'] == 'FILLED':
                        order_data.state = OrderState.Filled
                        order_data.filled_amount = Decimal(binance_order_info['executedQty'])
                        order_data.order_time = datetime.utcfromtimestamp(1.0 * binance_order_info['time'] / 1000)
                        session.commit()
                        print("{}|OrderFilled|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                               order_data.trade_pair_id, order_data.combination,
                                                               order_data.market))
                elif order_data.market == Market.OKEX:
                    okex_order_info = combination_obj.okex_trade_api.get_order(symbol=order_data.symbol,
                                                                               order_id=order_data.order_id)[0]
                    print order_data.query_amount, order_data.query_price, okex_order_info
                    if okex_order_info['status'] == 2:
                        order_data.state = OrderState.Filled
                        if order_data.trade_side == TradeSide.SIDE_BUY:
                            order_data.filled_amount = Decimal(okex_order_info['deal_amount']) / \
                                                       Decimal(okex_order_info['avg_price'])
                        else:
                            order_data.filled_amount = Decimal(okex_order_info['deal_amount']) * \
                                                       Decimal(okex_order_info['avg_price'])
                        order_data.order_time = datetime.utcfromtimestamp(1.0 * okex_order_info['create_date'] / 1000)
                        session.commit()
                        print("{}|OrderFilled|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                               order_data.trade_pair_id, order_data.combination,
                                                               order_data.market))
                # 1s最多一次操作
                time.sleep(1)
        except Exception as e:
            session.rollback()
            print("{}|TaskError|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                              e.message, traceback.format_exc()))
            try:
                ExceptionInfoModel(host=ip, source='CHECK_ORDER', message=e.message,
                                   log_time=datetime.utcnow()).add()
            except:
                pass
            # 重开对象
            session.close()
            session = get_dbsession()
            obj_dict = dict()
        print("{}|WaitForNextTurn".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
        # 休息1分钟
        time.sleep(60)


if __name__ == '__main__':
    run()
