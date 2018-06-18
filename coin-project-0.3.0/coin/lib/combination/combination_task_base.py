# -*- coding=utf-8 -*-
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import json
import time
from coin.lib.utils import get_redis_key
from coin.lib.config import BOOK_TIMEOUT, REBALANCE_THRESHOLD
from coin.lib.combination.combination import Combination


class CombinationTaskBase(object):

    def __init__(self, rds, id=None, combination=None):
        """
        用id或者组合来初始化，优先id
        :param id:
        :param combination:
        """
        if id is not None:
            self.combination = Combination.fetch_by_id(id)
        else:
            self.combination = Combination.fetch_by_combination(combination)
        self.first_market = self.combination.first_market
        self.second_market = self.combination.second_market
        self.rds = rds
        self.first_market_trade_api = None
        self.second_market_trade_api = None
        self.first_market_account = dict()
        self.second_market_account = dict()
        self.trader = None
        self.current_data_version = dict()
        self.account_fetch_time = time.time()
        self.initialize()

    def initialize(self):
        """
        初始化或者出异常之后重新初始化
        1. 赋值两个api
        2. 赋值trader
        3. 赋值两个account
        :return:
        """
        raise NotImplementedError

    def get_account(self):
        """
        获取账号
        :return:
        """
        self.get_first_market_account()
        self.get_second_market_account()
        self.account_fetch_time = time.time()

    def get_first_market_account(self):
        """
        火币account，注意get account不要和trade并发
        :return: account数据
        """
        raise NotImplementedError

    def get_second_market_account(self):
        """
        币安account
        :return:
        """
        raise NotImplementedError

    def find_profit(self, bids_info, asks_info):
        """
        寻找获利空间
        :param bids_info: [[price, amount], [price_amoun] ... ] 按照买价从高到低排序
        :param asks_info: [[price, amount], [price_amoun] ... ] 按照卖价从低到高排序
        :return: bid_price, ask_price, amount
        """
        index_bid, index_ask = 0, 0
        bid_price, ask_price, amount = Decimal('0.0'), Decimal('0.0'), Decimal('0.0')
        compute_bid_info = deepcopy(bids_info)
        compute_ask_info = deepcopy(asks_info)
        while index_bid < len(compute_bid_info) and index_ask < len(compute_ask_info):
            # 可获利，看看能成交数量多少
            if (compute_bid_info[index_bid][0] - compute_ask_info[index_ask][0]) / \
                    (compute_bid_info[index_bid][0] + compute_ask_info[index_ask][0]) * 2 > \
                    self.combination.trade_threshold:
                bid_price = compute_bid_info[index_bid][0]
                ask_price = compute_ask_info[index_ask][0]
                if compute_ask_info[index_ask][1] > compute_bid_info[index_bid][1]:
                    amount += compute_bid_info[index_bid][1]
                    compute_ask_info[index_ask][1] -= compute_bid_info[index_bid][1]
                    compute_bid_info[index_bid][1] = 0.0
                    index_bid += 1
                else:
                    amount += compute_ask_info[index_ask][1]
                    compute_bid_info[index_bid][1] -= compute_ask_info[index_ask][1]
                    compute_ask_info[index_ask][1] = 0.0
                    index_ask += 1
            else:
                break
        return bid_price, ask_price, amount

    def frozen_check(self):
        """
        如果冻结到已经数额，则不触发再平衡，如果超过一定比例，则不进行交易
        :return:
        """
        trade, rebalance = True, True
        first_market_small_frozen = self.first_market_account.get('{}_frozen'.format(self.combination.small_coin),
                                                                  Decimal('0'))
        second_market_small_frozen = self.second_market_account.get('{}_frozen'.format(self.combination.small_coin),
                                                                    Decimal('0'))
        first_market_big_frozen = self.first_market_account.get('{}_frozen'.format(self.combination.big_coin),
                                                                Decimal('0'))
        second_market_big_frozen = self.second_market_account.get('{}_frozen'.format(self.combination.big_coin),
                                                                  Decimal('0'))
        if first_market_big_frozen > Decimal('0.001') or second_market_big_frozen > Decimal('0.001'):
            rebalance = False
        if first_market_small_frozen > Decimal('0.01') or second_market_small_frozen > Decimal('0.01'):
            rebalance = False
        # 冻结超过一边的33%就不进行交易
        if first_market_big_frozen / self.combination.big_coin_amount * 2 > Decimal('0.33') \
                or second_market_big_frozen / self.combination.big_coin_amount * 2 > Decimal('0.33'):
            trade = False
        if first_market_small_frozen / self.combination.small_coin_amount * 2 > Decimal('0.33') \
                or second_market_small_frozen / self.combination.small_coin_amount * 2 > Decimal('0.33'):
            trade = False
        return trade, rebalance

    def coin_supplement(self):
        """
        补充货币，例如BNB等
        :return:
        """
        return

    def run(self):
        """
        运行
        :return:
        """
        if_trade, if_rebalance = self.frozen_check()
        if if_trade is False:
            print("{}|FrozenOverFLow|{}|{}|{}|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),  self.first_market,
                         self.first_market_account, self.second_market, self.second_market_account))
            # 被冻结太多了，休息会
            time.sleep(10)
            self.get_account()
            return
        pipe = self.rds.pipeline(transaction=False)
        redis_key1 = get_redis_key(market=self.first_market, coin1=self.combination.small_coin,
                                   coin2=self.combination.big_coin)
        pipe.hgetall(redis_key1)
        redis_key2 = get_redis_key(market=self.second_market, coin1=self.combination.small_coin,
                                   coin2=self.combination.big_coin)
        pipe.hgetall(redis_key2)
        res = pipe.execute()
        # 数据可能不存在
        if not res[0]:
            print("{}|BookNotExist|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                    self.first_market, self.combination.small_coin,
                                                    self.combination.big_coin))
            return
        if not res[1]:
            print("{}|BookNotExist|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                    self.second_market, self.combination.small_coin,
                                                    self.combination.big_coin))
            return
        # 先把bids和asks数据从字符串转换回去
        # 版本统一用version指代
        # 时间戳统一用ts
        for item in res:
            item['ts'] = int(item['ts'])
            if 'lastUpdateId' in item:
                item['version'] = int(item['lastUpdateId'])
            if 'version' in item:
                item['version'] = int(item['version'])
            item['bids'] = json.loads(item['bids'])
            item['asks'] = json.loads(item['asks'])
        # 数据可能已经处理过了，还没有更新
        # 这种情况很多，就不用打日志了
        if redis_key1 in self.current_data_version and redis_key2 in self.current_data_version \
                and (self.current_data_version[redis_key1] >= res[0]['version']
                     and self.current_data_version[redis_key2] >= res[1]['version']):
            # print("{}|DataNotUpdate|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            #                                       coin1, coin2))
            return
        else:  # 缓存数据
            self.current_data_version[redis_key1] = res[0]['version']
            self.current_data_version[redis_key2] = \
                res[1]['lastUpdateId'] if 'lastUpdateId' in res[1] else res[1]['version']
        # 数据可能超时，注意，存储的数据是毫秒级的
        current = int(time.time() * 1000)
        if current - res[0]['ts'] > BOOK_TIMEOUT * 1000:
            print("{}|BookTimeOut|{}|{}|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                         self.first_market, self.combination.small_coin,
                                                         self.combination.big_coin, current, res[0]['ts']))
            return
        if current - res[1]['ts'] > BOOK_TIMEOUT * 1000:
            print("{}|BookTimeOut|{}|{}|{}|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                         self.second_market, self.combination.small_coin,
                                                         self.combination.big_coin, current, res[1]['ts']))
            return
        # 比较差价
        # 先转换为Decimal
        for res_index in xrange(2):
            for type_index in ['bids', 'asks']:
                res[res_index][type_index] = [[Decimal(str(item[0])), Decimal(str(item[1]))]
                                              for item in res[res_index][type_index]]
        first_market_depth_time = res[0]['ts']
        second_market_depth_time = res[1]['ts']
        # bids买，第一位为买小币的最高价；asks卖，第一位为卖小币的最低价
        bid_price, ask_price, amount = self.find_profit(res[0]['bids'], res[1]['asks'])
        if amount > 0:  # 有机会了
            self.trader.first_market_sell_second_market_market_buy(first_market_account=self.first_market_account,
                                                                   second_market_account=self.second_market_account,
                                                                   bid_price=bid_price,
                                                                   ask_price=ask_price,
                                                                   amount=amount,
                                                                   first_market_bids_depth=res[0]['bids'],
                                                                   second_market_asks_depth=res[1]['asks'],
                                                                   first_market_depth_time=first_market_depth_time,
                                                                   second_market_depth_time=second_market_depth_time)
        # 不可能出现一边买大于另一边卖，同时一边的卖低于另一边的买
        bid_price, ask_price, amount = self.find_profit(res[1]['bids'], res[0]['asks'])
        if amount > 0:
            self.trader.first_market_buy_second_market_market_sell(first_market_account=self.first_market_account,
                                                                   second_market_account=self.second_market_account,
                                                                   bid_price=bid_price,
                                                                   ask_price=ask_price,
                                                                   amount=amount,
                                                                   first_market_asks_depth=res[0]['asks'],
                                                                   second_market_bids_depth=res[1]['bids'],
                                                                   first_market_depth_time=first_market_depth_time,
                                                                   second_market_depth_time=second_market_depth_time)
        if if_rebalance is True:
            if self.first_market_account[self.combination.small_coin] \
                    < self.combination.small_coin_amount * REBALANCE_THRESHOLD:
                self.trader.first_market_small_coin_rebalance(first_market_account=self.first_market_account,
                                                              second_market_account=self.second_market_account,
                                                              second_market_bid_info=res[1]['bids'],
                                                              first_market_ask_info=res[0]['asks'],
                                                              small_point_amount=self.combination.small_coin_amount,
                                                              first_market_depth_time=first_market_depth_time,
                                                              second_market_depth_time=second_market_depth_time)
            elif self.second_market_account[self.combination.small_coin] < \
                    self.combination.small_coin_amount * REBALANCE_THRESHOLD:
                self.trader.second_market_small_coin_rebalance(first_market_account=self.first_market_account,
                                                               second_market_account=self.second_market_account,
                                                               first_market_bid_info=res[0]['bids'],
                                                               second_market_ask_info=res[1]['asks'],
                                                               small_point_amount=self.combination.small_coin_amount,
                                                               first_market_depth_time=first_market_depth_time,
                                                               second_market_depth_time=second_market_depth_time)
            # 小币调整应该是罕见的才对，先不限制只有没交易才小币调整
            self.trader.small_coin_adjust(first_market_account=self.first_market_account,
                                          second_market_account=self.second_market_account,
                                          small_coin_amount=self.combination.small_coin_amount,
                                          first_market_depth_info=res[0], second_market_depth_info=res[1],
                                          first_market_depth_time=first_market_depth_time,
                                          second_market_depth_time=second_market_depth_time)
        if time.time() - self.account_fetch_time > 600:  # 每10分钟获取account
            self.get_account()
            # 如果有需要补充货币，没10分钟处理一次
            self.coin_supplement()
