# -*- coding=utf-8 -*-
"""
获取交易数据
"""
from collections import defaultdict
from commandr import Run, command
from datetime import datetime
from decimal import Decimal
import time
import traceback
from coin.model.base import get_dbsession
from coin.model.account_data import AccountCoinInfoModel
from coin.lib.combination.combination import Combination
from coin.lib.api.binance import BinanceTradeApi
from coin.lib.combination.huobi_binance_trade_task import HuobiBinanceCombinationTask
from coin.lib.combination.okex_binance_trade_task import OKExBinanceCombinationTask
from coin.lib.combination.huobi_okex_trade_task import HuobiOKExCombinationTask
from coin.model.combination import CombinationModel
from coin.lib.utils import Market, Status, ip
from coin.model.exception_info import ExceptionInfoModel


interval = 600  # 10分钟一次


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


@command('start')
def start_combination(name):
    """
    开始一个组合，并记录account
    :param name:
    :return:
    """
    session = get_dbsession()
    try:
        combination_obj = Combination.fetch_by_combination(name)
        fetch_combination_account(combination_obj, Status.Start)
        _db = session.query(CombinationModel).filter_by(combination=name).one_or_none()
        _db.status = Status.Active
        session.commit()
    except:
        session.rollback()
        raise
    print("{}|StartCombination|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), name))


@command('end')
def end_combination(name):
    """
    结束组合
    :param name:
    :return:
    """
    session = get_dbsession()
    try:
        combination_obj = Combination.fetch_by_combination(name)
        fetch_combination_account(combination_obj, Status.End)
        _db = session.query(CombinationModel).filter_by(combination=name).one_or_none()
        _db.status = Status.End
        session.commit()
    except:
        session.rollback()
        raise
    print("{}|EndCombination|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), name))


def fetch_combination_account(combination, status):
    """
    获取组合的账号信息
    :param combination:
    :type combination: Combination
    :param status:
    :return:
    """
    task_obj = get_task_object(None, combination.combination)
    task_obj.get_account()
    first_market_big_coin = task_obj.first_market_account[combination.big_coin]
    first_market_small_coin = task_obj.first_market_account[combination.small_coin]
    second_market_big_coin = task_obj.second_market_account[combination.big_coin]
    second_market_small_coin = task_obj.second_market_account[combination.small_coin]
    time.sleep(1)
    btc_price = Decimal('0')
    bnb_price = Decimal('0')
    symbol_price = Decimal('0')
    big_coin_btc_price = Decimal('0')
    # 使用币安的价格
    price_list = BinanceTradeApi('', '').get_orderbook_tickers()
    binance_symbol = '{}{}'.format(combination.small_coin, combination.big_coin).upper()
    big_coin_btc_symbol = '{}{}'.format(combination.big_coin, 'btc').upper()
    for item in price_list:
        if item['symbol'] == 'BTCUSDT':
            btc_price = (Decimal(item['bidPrice']) + Decimal(item['askPrice'])) / 2
        elif item['symbol'] == 'BNBBTC':
            bnb_price = (Decimal(item['bidPrice']) + Decimal(item['askPrice'])) / 2
        elif item['symbol'] == binance_symbol:
            symbol_price = (Decimal(item['bidPrice']) + Decimal(item['askPrice'])) / 2
        elif combination.big_coin.lower() != 'btc' and item['symbol'] == big_coin_btc_symbol:
            big_coin_btc_price = (Decimal(item['bidPrice']) + Decimal(item['askPrice'])) / 2
        elif combination.big_coin.lower() == 'btc':
            big_coin_btc_price = Decimal('1')
    # Account中间都是小写
    if combination.first_market == Market.BINANCE:
        bnb = task_obj.first_market_account.get('bnb', Decimal(0))
    elif combination.second_market == Market.BINANCE:
        bnb = task_obj.second_market_account.get('bnb', Decimal(0))
    else:
        bnb = Decimal('0')
    if combination.first_market == Market.HUOBI:
        huobi_point = task_obj.first_market_trade_api.get_huobi_point()
    elif combination.second_market == Market.HUOBI:
        huobi_point = task_obj.second_market_trade_api.get_huobi_point()
    else:
        huobi_point = Decimal('0')

    AccountCoinInfoModel(combination=combination.combination,
                         first_market_big_coin=first_market_big_coin,
                         first_market_small_coin=first_market_small_coin,
                         second_market_big_coin=second_market_big_coin,
                         second_market_small_coin=second_market_small_coin,
                         big_coin_total=first_market_big_coin+second_market_big_coin,
                         small_coin_total=first_market_small_coin+second_market_small_coin,
                         bnb=bnb,
                         huobi_point=huobi_point,
                         symbol_price=symbol_price,
                         bnb_price=bnb_price,
                         btc_price=btc_price,
                         status=status,
                         big_coin_btc_price=big_coin_btc_price,
                         log_time=datetime.utcnow()).add()
    print("{}|GetAccount|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                    combination.combination))


@command('fetch')
def run():
    while 1:
        # 整点运行
        current = time.time()
        time.sleep(interval - current % interval)
        combination_list = Combination.all()
        try:
            for combination in combination_list:
                if combination.status != Status.Active:  # 不活跃的组合不再运行
                    continue
                # 获取account，避免频繁调用api
                fetch_combination_account(combination=combination, status=Status.Active)
                time.sleep(1)
        except Exception as e:
            try:
                ExceptionInfoModel(host=ip, source='FETCH_ACCOUNT_DATA', message=e.message,
                                   log_time=datetime.utcnow()).add()
            except:
                pass
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            time.sleep(5)


if __name__ == '__main__':
    Run()
