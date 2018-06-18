# -*- coding=utf-8 -*-
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from coin.lib.config import BNB_SUPPLEMENT, BNB_SUPPLEMENT_THRESHOLD
from coin.lib.combination.combination_task_base import CombinationTaskBase
from coin.lib.coin_exception import NotEnoughCoinError, InitialError
from coin.lib.api.okex import OKExTradeApi
from coin.lib.api.binance import BinanceTradeApi
from coin.lib.trader.okex_binance_trader import OKExBinanceTrader


class OKExBinanceCombinationTask(CombinationTaskBase):

    def __init__(self, rds, id=None, combination=None):
        """
        用id或者组合来初始化，优先id
        :param id:
        :param combination:
        """
        super(OKExBinanceCombinationTask, self).__init__(rds=rds, id=id, combination=combination)
        self.okex_trade_api = self.first_market_trade_api
        self.binance_trade_api = self.second_market_trade_api

    def get_trader(self):
        """
        获取trader
        :return:
        """
        trade_pair = '{}_{}'.format(self.combination.small_coin, self.combination.big_coin)
        trader_class = None
        trader_class_list = OKExBinanceTrader.__subclasses__()
        for item in trader_class_list:
            if item.__trade_pair__ == trade_pair:
                trader_class = item
        if trader_class is None:
            raise InitialError(u'can not find trader class for trade_pair {}'.format(trade_pair))
        return trader_class

    def initialize(self):
        """
        初始化或者出异常之后重新初始化
        :return:
        """
        self.first_market_trade_api = OKExTradeApi(api_key=self.combination.first_market_api_key,
                                                   api_secret=self.combination.first_market_api_secret)
        self.second_market_trade_api = BinanceTradeApi(api_key=self.combination.second_market_api_key,
                                                       api_secret=self.combination.second_market_api_secret)
        self.first_market_account = dict()
        self.second_market_account = dict()
        self.trader = self.get_trader()(self.combination.combination, self.first_market_trade_api,
                                        self.second_market_trade_api)

    def get_first_market_account(self):
        """
        火币account，注意get account不要和trade并发
        :return: account数据
        """
        res = self.first_market_trade_api.get_account()
        tmp_account_data = defaultdict(Decimal)
        for coin, amount in res['free'].items():
            balance = Decimal(amount)
            if balance > 0:
                tmp_account_data[coin] = balance
        for coin, amount in res['freezed'].items():
            balance = Decimal(amount)
            if balance > 0:
                tmp_account_data['{}_frozen'.format(coin)] = balance
        self.first_market_account = tmp_account_data
        del tmp_account_data
        if not self.first_market_account.get(self.combination.small_coin):
            self.first_market_account[self.combination.small_coin] = Decimal('0')
        if not self.first_market_account.get(self.combination.big_coin):
            self.first_market_account[self.combination.big_coin] = Decimal('0')
        print("{}|GetOKExAccount|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                            self.first_market_account))

    def get_second_market_account(self):
        """
        币安account
        :return:
        """
        res = self.second_market_trade_api.get_account()
        tmp_account_data = dict()
        if not res['canTrade']:  # 无法交易
            return
        for item in res['balances']:
            balance = Decimal(item['free'])
            frozen = Decimal(item['locked'])
            if balance > 0:  # 有币
                # 统一使用小写
                tmp_account_data[item['asset'].lower()] = balance
            if frozen > 0:
                tmp_account_data['{}_frozen'.format(item['asset'].lower())] = frozen
        self.second_market_account = tmp_account_data
        del tmp_account_data
        if not self.second_market_account.get(self.combination.small_coin):
            self.second_market_account[self.combination.small_coin] = Decimal('0')
        if not self.second_market_account.get(self.combination.big_coin):
            self.second_market_account[self.combination.big_coin] = Decimal('0')
        print("{}|GetBinanceAccount|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                               self.second_market_account))

    def coin_supplement(self):
        """
        补充bnb
        :return:
        """
        if self.second_market_account.get('bnb', Decimal('0')) < BNB_SUPPLEMENT_THRESHOLD:
            self.trader.bnb_supplement(BNB_SUPPLEMENT)

