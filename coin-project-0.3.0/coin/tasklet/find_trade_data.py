# -*- coding=utf-8 -*-
"""
交易相关
"""
from datetime import datetime
import time
import traceback
from redis import Redis
from commandr import command, Run
from coin.lib.coin_exception import NotEnoughCoinError
from coin.lib.utils import Market, Status, ip
from coin.lib.combination.combination import Combination
from coin.lib.combination.huobi_binance_trade_task import HuobiBinanceCombinationTask
from coin.lib.combination.okex_binance_trade_task import OKExBinanceCombinationTask
from coin.lib.combination.huobi_okex_trade_task import HuobiOKExCombinationTask
from coin.model.exception_info import ExceptionInfoModel


@command('run')
def run(combination):
    """
    coin对，都是小币在前，大币在后
    :param combination: 组合名称的list
    :return:
    """
    rds = Redis()
    combination_obj = Combination.fetch_by_combination(combination)
    if combination_obj.status != Status.Active:
        print('{}|CombinationNotActive|'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
        return
    if combination_obj.first_market == Market.HUOBI and combination_obj.second_market == Market.BINANCE:
        task_obj = HuobiBinanceCombinationTask(rds=rds, combination=combination)
    elif combination_obj.first_market == Market.OKEX and combination_obj.second_market == Market.BINANCE:
        task_obj = OKExBinanceCombinationTask(rds=rds, combination=combination)
    elif combination_obj.first_market == Market.HUOBI and combination_obj.second_market == Market.OKEX:
        task_obj = HuobiOKExCombinationTask(rds=rds, combination=combination)
    else:
        raise ValueError('Unsupported combination {}'.format(combination))
    # 获取一下account
    task_obj.get_account()
    # 检查Account
    if not task_obj.first_market_account.get(task_obj.combination.small_coin):
        raise NotEnoughCoinError('Not enough {} in {}'.format(task_obj.combination.small_coin, task_obj.first_market))
    if not task_obj.first_market_account.get(task_obj.combination.big_coin):
        raise NotEnoughCoinError('Not enough {} in {}'.format(task_obj.combination.big_coin, task_obj.first_market))
    if not task_obj.second_market_account.get(task_obj.combination.small_coin):
        raise NotEnoughCoinError('Not enough {} in {}'.format(task_obj.combination.small_coin, task_obj.second_market))
    if not task_obj.second_market_account.get(task_obj.combination.big_coin):
        raise NotEnoughCoinError('Not enough {} in {}'.format(task_obj.combination.big_coin, task_obj.second_market))

    while 1:
        try:
            task_obj.run()
            # 现在遇到异常先使用退出的方法
            if task_obj.trader.trade_exception is True:
                print('{}|MeetTradeException|'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                # 睡10s
                # 重新生成API
                time.sleep(10)
                task_obj.initialize()
                task_obj.get_account()
                task_obj.trader.trade_exception = False
        except Exception as e:
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            try:
                ExceptionInfoModel(host=ip, source='FETCH_TRADE_DATA', message=e.message,
                                   log_time=datetime.utcnow()).add()
            except:
                pass
            # 睡10s
            time.sleep(10)
            # 重新生成API
            task_obj.initialize()
            task_obj.get_account()
            task_obj.trader.trade_exception = False


if __name__ == '__main__':
    # test_coin_pair_list = [('IOST', 'BTC'), ('TRX', 'ETH')]
    # run_combination_list = ['HUOBI_BINANCE_IOST_BTC_ZHIFU', 'HUOBI_BINANCE_DGD_ETH_ZHIFU', 'HUOBI_BINANCE_TRX_ETH_ZHIFU']
    # run(run_combination_list)
    Run()
