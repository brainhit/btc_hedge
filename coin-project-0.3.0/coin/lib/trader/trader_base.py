# -*- coding=utf-8 -*-
from datetime import datetime
import json
import time
from threading import Thread
from coin.lib.config import PRECISE, REBALANCE_THRESHOLD, SMALL_COIN_SUPPLEMENT_HIGH_THRESHOLD, \
    SMALL_COIN_SUPPLEMENT_LOW_THRESHOLD
from coin.lib.utils import OrderType, Market, TradeSide, TradeTarget, get_trade_amount, ip
from coin.lib.trade_info import SqlTraderInfo
from coin.model.exception_info import ExceptionInfoModel
from decimal import Decimal, ROUND_DOWN


class TraderBase(object):

    __trade_pair__ = None  # 形式为小币_大币

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    def __init__(self, combination, first_trade_api, second_trader_api, first_market, second_market,
                 small_coin, big_coin, first_market_symbol, second_market_symbol, trade_amount_threshold):
        self.combination = combination  # str，代表组合的字符串
        self.first_trade_api = first_trade_api
        self.second_trader_api = second_trader_api
        self.first_market = first_market
        self.second_market = second_market
        self.trade_exception = False  # 是否发生了trade_exception
        self.small_coin = small_coin
        self.big_coin = big_coin
        self.first_market_symbol = first_market_symbol
        self.second_market_symbol = second_market_symbol
        self.trade_amount_threshold = trade_amount_threshold
        self.first_market_buy_precise = PRECISE[self.first_market][self.__trade_pair__][TradeSide.SIDE_BUY]
        self.first_market_sell_precise = PRECISE[self.first_market][self.__trade_pair__][TradeSide.SIDE_SELL]
        self.second_market_buy_precise = PRECISE[self.second_market][self.__trade_pair__][TradeSide.SIDE_BUY]
        self.second_market_sell_precise = PRECISE[self.second_market][self.__trade_pair__][TradeSide.SIDE_SELL]
        self.frozen_symbol = '{}_frozen'.format(self.small_coin)
        self.big_coin_frozen_symbol = '{}_frozen'.format(self.big_coin)

    def depth_amount_check(self, amount):
        """
        从深度信息获取的amount检查
        :param amount: 深度信息读取出来允许进行多少交易
        :return:
        """
        if amount < self.trade_amount_threshold:
            return False
        return True

    def trade_amount_check(self, amount):
        """
        检查amount
        :param amount: 当前能够交易的amount
        :return:
        """
        if amount < self.trade_amount_threshold:
            return False
        return True

    @staticmethod
    def find_trade_price(target_amount, depth_info):
        """
        寻找交易价格
        :param target_amount:
        :type target_amount: Decimal
        :param depth_info: [(price, amount), (), ()]
        :return: price
        """
        index, tmp_total = 0, Decimal(0)
        while index < len(depth_info):
            if tmp_total + depth_info[index][1] >= target_amount:
                return depth_info[index][0]
            tmp_total += depth_info[index][1]
            index += 1
        return depth_info[-1][0]

    def _first_market_send_buy_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        raise NotImplementedError

    def _first_market_send_sell_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        raise NotImplementedError

    def _second_market_send_buy_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        raise NotImplementedError

    def _second_market_send_sell_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        raise NotImplementedError

    def _first_market_buy(self, trade_pair_id, symbol, amount, price, trade_target, first_market_asks_depth,
                          depth_time, create_time):
        """
        第一个市场买
        :param trade_pair_id:
        :param symbol:
        :param amount:
        :param price:
        :param trade_target:
        :param first_market_asks_depth:
        :param depth_time:
        :param create_time:
        :return:
        """
        # Decimal类型无法Json序列化
        first_market_asks_depth_str = json.dumps([[str(item[0]), str(item[1])] for item in first_market_asks_depth])
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        try:
            order_id = self._first_market_send_buy_request(symbol=symbol, order_type=OrderType.BuyMarket,
                                                           amount=amount)
            SqlTraderInfo.add_new_trade(combination=self.combination, order_id=order_id, trade_pair_id=trade_pair_id,
                                        market=self.first_market,
                                        symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                        trade_side=self.SIDE_BUY,
                                        trade_target=trade_target, amount=amount, price=price,
                                        depth_str=first_market_asks_depth_str, depth_time=depth_time,
                                        create_time=create_time)
            print("{}|TradeInfo|{}|{}|{}|{}|{}".format(current_datetime_str,
                                                       self.first_market, trade_pair_id, self.SIDE_BUY, amount, price))
        except Exception as e:
            print("{}|TradeError|{}|{}|{}".format(current_datetime_str,
                                                  self.first_market, trade_pair_id, e.message))
            try:
                SqlTraderInfo.add_exception_trade(combination=self.combination, order_id=None,
                                                  trade_pair_id=trade_pair_id,
                                                  market=self.first_market,
                                                  symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                                  trade_side=self.SIDE_BUY,
                                                  trade_target=trade_target, amount=amount,
                                                  price=price, depth_str=first_market_asks_depth_str,
                                                  exception_message=e.message, depth_time=depth_time,
                                                  create_time=create_time)
                ExceptionInfoModel(host=ip, source=self.combination, message=e.message,
                                   log_time=datetime.utcnow()).add()
            except Exception as e:
                print("{}|SqlError|{}|{}|{}".format(current_datetime_str,
                                                    self.first_market, trade_pair_id, e.message))
            self.trade_exception = True
        finally:
            SqlTraderInfo.clear_session()

    def _first_market_sell(self, trade_pair_id, symbol, amount, price, trade_target, first_market_bids_depth,
                           depth_time, create_time):
        """
        第一个市场卖
        :param trade_pair_id:
        :param symbol:
        :param amount:
        :param price:
        :type price: Decimal
        :param trade_target:
        :param first_market_bids_depth [(), ()] 火币的bid深度信息
        :return:
        """
        # Decimal类型无法Json序列化
        first_market_bids_depth_str = json.dumps([[str(item[0]), str(item[1])] for item in first_market_bids_depth])
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        try:
            order_id = self._first_market_send_sell_request(symbol=symbol, order_type=OrderType.SellMarket,
                                                            amount=amount)
            SqlTraderInfo.add_new_trade(combination=self.combination, order_id=order_id, trade_pair_id=trade_pair_id,
                                        market=self.first_market,
                                        symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                        trade_side=self.SIDE_SELL,
                                        trade_target=trade_target, amount=amount, price=price,
                                        depth_str=first_market_bids_depth_str, depth_time=depth_time,
                                        create_time=create_time)
            print("{}|TradeInfo|{}|{}|{}|{}".format(current_datetime_str,
                                                    self.first_market, trade_pair_id, self.SIDE_SELL, amount))
        except Exception as e:
            print("{}|TradeError|{}|{}|{}".format(current_datetime_str,
                                                  self.first_market, trade_pair_id, e.message))
            try:
                SqlTraderInfo.add_exception_trade(combination=self.combination, order_id=None,
                                                  trade_pair_id=trade_pair_id,
                                                  market=self.first_market,
                                                  symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                                  trade_side=self.SIDE_SELL,
                                                  trade_target=trade_target, amount=amount,
                                                  price=price, depth_str=first_market_bids_depth_str,
                                                  exception_message=e.message, depth_time=depth_time,
                                                  create_time=create_time)
                ExceptionInfoModel(host=ip, source=self.combination, message=e.message,
                                   log_time=datetime.utcnow()).add()
            except Exception as e:
                print("{}|SqlError|{}|{}|{}".format(current_datetime_str,
                                                    self.first_market, trade_pair_id, e.message))
            self.trade_exception = True
        finally:
            SqlTraderInfo.clear_session()

    def _second_market_buy(self, trade_pair_id, symbol, amount, price, trade_target, second_market_asks_depth,
                           depth_time, create_time):
        """
        第二市场买
        :param trade_pair_id:
        :param symbol:
        :param amount:
        :type amount: Decimal
        :param price:
        :type price: Decimal
        :param trade_target:
        :param second_market_asks_depth: 币安卖价深度信息
        :return:
        """
        # Decimal类型无法Json序列化
        second_market_asks_depth_str = json.dumps([[str(item[0]), str(item[1])] for item in second_market_asks_depth])
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        try:
            order_id = self._second_market_send_buy_request(symbol=symbol, amount=amount,
                                                            order_type=OrderType.BuyMarket)
            SqlTraderInfo.add_new_trade(combination=self.combination, order_id=order_id,
                                        trade_pair_id=trade_pair_id,
                                        market=self.second_market,
                                        symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                        trade_side=self.SIDE_BUY,
                                        trade_target=trade_target, amount=amount, price=price,
                                        depth_str=second_market_asks_depth_str, depth_time=depth_time,
                                        create_time=create_time)
            print("{}|TradeInfo|{}|{}|{}|{}".format(current_datetime_str,
                                                    self.second_market, trade_pair_id, self.SIDE_BUY, amount))
        except Exception as e:
            print("{}|TradeError|{}|{}|{}".format(current_datetime_str,
                                                  self.second_market, trade_pair_id, e.message))
            try:
                SqlTraderInfo.add_exception_trade(combination=self.combination, order_id=None,
                                                  trade_pair_id=trade_pair_id,
                                                  market=self.second_market,
                                                  symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                                  trade_side=self.SIDE_BUY,
                                                  trade_target=trade_target, amount=amount,
                                                  price=price, depth_str=second_market_asks_depth_str,
                                                  exception_message=e.message, depth_time=depth_time,
                                                  create_time=create_time)
                ExceptionInfoModel(host=ip, source=self.combination, message=e.message,
                                   log_time=datetime.utcnow()).add()
            except Exception as e:
                print("{}|SqlError|{}|{}|{}".format(current_datetime_str,
                                                    self.second_market, trade_pair_id, e.message))
            self.trade_exception = True
        finally:
            SqlTraderInfo.clear_session()

    def _second_market_sell(self, trade_pair_id, symbol, amount, price, trade_target, second_market_bids_depth,
                            depth_time, create_time):
        """
        第二市场卖
        :param trade_pair_id:
        :param symbol:
        :param amount:
        :param price:
        :param trade_target:
        :param second_market_bids_depth: 币安买价深度信息
        :return:
        """
        # Decimal类型无法Json序列化
        second_market_bids_depth_str = json.dumps([[str(item[0]), str(item[1])] for item in second_market_bids_depth])
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        try:
            order_id = self._second_market_send_sell_request(symbol=symbol, amount=amount,
                                                             order_type=OrderType.SellMarket)
            SqlTraderInfo.add_new_trade(combination=self.combination, order_id=order_id,
                                        trade_pair_id=trade_pair_id,
                                        market=self.second_market,
                                        symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                        trade_side=self.SIDE_SELL,
                                        trade_target=trade_target, amount=amount, price=price,
                                        depth_str=second_market_bids_depth_str, depth_time=depth_time,
                                        create_time=create_time)
            print("{}|TradeInfo|{}|{}|{}|{}".format(current_datetime_str,
                                                    self.second_market, trade_pair_id, self.SIDE_SELL, amount))
        except Exception as e:
            print("{}|TradeError|{}|{}|{}".format(current_datetime_str,
                                                  self.second_market, trade_pair_id, e.message))
            try:
                SqlTraderInfo.add_exception_trade(combination=self.combination, order_id=None,
                                                  trade_pair_id=trade_pair_id,
                                                  market=self.second_market,
                                                  symbol='{}{}'.format(self.small_coin, self.big_coin).lower(),
                                                  trade_side=self.SIDE_SELL,
                                                  trade_target=trade_target, amount=amount,
                                                  price=price, depth_str=second_market_bids_depth_str,
                                                  exception_message=e.message, depth_time=depth_time,
                                                  create_time=create_time)
                ExceptionInfoModel(host=ip, source=self.combination, message=e.message,
                                   log_time=datetime.utcnow()).add()
            except Exception as e:
                print("{}|SqlError|{}|{}|{}".format(current_datetime_str,
                                                    self.second_market, trade_pair_id, e.message))
            self.trade_exception = True
        finally:
            SqlTraderInfo.clear_session()

    def _first_market_buy_second_market_sell_endpoint(self, buy_symbol, buy_amount, buy_price,
                                                      sell_symbol, sell_mouunt, sell_price, trade_target,
                                                      first_market_asks_depth, second_market_bids_depth,
                                                      first_market_depth_time, second_market_depth_time, create_time):
        """
        第一市场价买，第二市场价卖
        :param buy_symbol:
        :type buy_symbol: str
        :param buy_amount:
        :type buy_amount: Decimal
        :param buy_price:
        :param sell_symbol:
        :type sell_symbol: str
        :param sell_mouunt:
        :type sell_mouunt: Decimal
        :param sell_price:
        :param trade_target:
        :return:
        """
        trade_pair_id = '{}_{}_{}'.format(int(time.time()*1000), '{}_MARKET_BUY'.format(self.first_market),
                                          '{}_MARKET_SELL'.format(self.second_market))
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        t1 = Thread(target=self._first_market_buy, args=(trade_pair_id, buy_symbol, buy_amount,
                                                         buy_price, trade_target, first_market_asks_depth,
                                                         first_market_depth_time, create_time))
        t2 = Thread(target=self._second_market_sell, args=(trade_pair_id, sell_symbol, sell_mouunt,
                                                           sell_price, trade_target, second_market_bids_depth,
                                                           second_market_depth_time, create_time))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print("{}|Trade|PairID|{}|SellSymbol|{}|SellAmount|{}|BuySymbol|{}|BuyAmount|{}".
              format(current_datetime_str, trade_pair_id, sell_symbol,
                     sell_mouunt, buy_symbol, buy_amount))

    def _first_market_sell_second_market_buy_endpoint(self, sell_symbol, sell_mouunt, sell_price,
                                                      buy_symbol, buy_amount, buy_price, trade_target,
                                                      first_market_bids_depth, second_market_asks_depth,
                                                      first_market_depth_time, second_market_depth_time, create_time):
        """
        第一市场价卖，第二市场价买
        :param sell_symbol:
        :param sell_mouunt:
        :param sell_price:
        :param buy_symbol:
        :param buy_amount:
        :param buy_price:
        :param trade_target:
        :return:
        """
        trade_pair_id = '{}_{}_{}'.format(int(time.time()*1000), '{}_MARKET_SELL'.format(self.first_market),
                                          '{}_MARKET_BUY'.format(self.second_market))
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        t1 = Thread(target=self._first_market_sell, args=(trade_pair_id, sell_symbol, sell_mouunt,
                                                          sell_price, trade_target, first_market_bids_depth,
                                                          first_market_depth_time, create_time))
        t2 = Thread(target=self._second_market_buy, args=(trade_pair_id, buy_symbol, buy_amount,
                                                          buy_price, trade_target, second_market_asks_depth,
                                                          second_market_depth_time, create_time))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print("{}|Trade|PairID|{}|SellSymbol|{}|SellAmount|{}|BuySymbol|{}|BuyAmount|{}".
              format(current_datetime_str, trade_pair_id, sell_symbol,
                     sell_mouunt, buy_symbol, buy_amount))

    def _first_sell_pre_process(self, first_market_account, bid_price, first_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量，并修改account
        :param first_market_account:
        :param bid_price:
        :param first_market_amount:
        :return: first_market_trade_amount
        """
        raise NotImplementedError

    def _first_buy_pre_process(self, first_market_account, ask_price, first_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量，并修改account
        :param first_market_account:
        :param ask_price:
        :param first_market_amount:
        :return: first_market_trade_amount
        """
        raise NotImplementedError

    def _second_sell_pre_process(self, second_market_account, bid_price, second_market_amount):
        """
        预处理，得到实际作为交易参数的第二个市场的交易数量，并修改account
        :param second_market_account:
        :param bid_price:
        :param second_market_amount:
        :return: second_market_trade_amount
        """
        raise NotImplementedError

    def _second_buy_pre_process(self, second_market_account, ask_price, second_market_amount):
        """
        预处理，得到实际作为交易参数的第二个市场的交易数量，并修改account
        :param second_market_account:
        :param ask_price:
        :return: second_market_trade_amount
        """
        raise NotImplementedError

    def _first_sell_second_buy_pre_process(self, first_market_account, second_market_account,
                                           bid_price, ask_price, first_market_amount, second_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量和第二个市场的交易数量，并修改account
        :param first_market_account:
        :param second_market_account:
        :param first_market_amount:
        :param second_market_amount:
        :return: first_market_trade_amount, second_market_trade_amount
        """
        first_market_trade_amount = self._first_sell_pre_process(
            first_market_account=first_market_account, bid_price=bid_price, first_market_amount=first_market_amount)
        second_market_trade_amount = self._second_buy_pre_process(
            second_market_account=second_market_account, ask_price=ask_price, second_market_amount=second_market_amount)
        return first_market_trade_amount, second_market_trade_amount

    def _first_buy_second_sell_pre_process(self, first_market_account, second_market_account,
                                           bid_price, ask_price, first_market_amount, second_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量和第二个市场的交易数量，并修改account
        :param first_market_account:
        :param second_market_account:
        :param first_market_amount:
        :param second_market_amount:
        :return: first_market_trade_amount, second_market_trade_amount
        """
        first_market_trade_amount = self._first_buy_pre_process(
            first_market_account=first_market_account, ask_price=ask_price, first_market_amount=first_market_amount)
        second_market_trade_amount = self._second_sell_pre_process(
            second_market_account=second_market_account, bid_price=bid_price, second_market_amount=second_market_amount)
        return first_market_trade_amount, second_market_trade_amount

    def first_market_buy_second_market_market_sell(self, first_market_account, second_market_account, bid_price,
                                                   ask_price, amount, first_market_asks_depth,
                                                   second_market_bids_depth, first_market_depth_time,
                                                   second_market_depth_time):
        """
        从第一个市场买小币，在第二个市场卖小币
        :param first_market_account: 火币的火币数量
        :type first_market_account:
        :param second_market_account: 币安的火币数量
        :param bid_price:
        :param ask_price:
        :param amount:
        :type amount: Decimal
        :param first_market_asks_depth [(), ()]
        :param second_market_bids_depth
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        if self.depth_amount_check(amount) is False:
            print("{}|DepthAmountInvalid|{}|{}|{}_ASKS|{}|{}_BIDS|{}|AMOUNT|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self.small_coin, self.big_coin,
                         self.first_market, bid_price, self.second_market, ask_price, amount))
            return
        trade_amount = get_trade_amount(amount=amount)
        # 悲观做法，乘一个系数，避免币不够
        # 第一个市场的大币够不够
        if first_market_account[self.big_coin] < trade_amount * ask_price / Decimal('0.95'):
            trade_amount = first_market_account[self.big_coin] / ask_price * Decimal('0.95')
        # 看看自己在第二个市场持有的小币够不够卖的
        if second_market_account[self.small_coin] < trade_amount / Decimal('0.95'):
            trade_amount = second_market_account[self.small_coin] * Decimal('0.95')
        # 交易量不够
        if self.trade_amount_check(trade_amount) is False:
            print("{}|TradeAmountInvalid|{}|{}|{}_ASKS|{}|{}_BIDS|{}|AMOUNT|{}TRADEAMOUNT|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self.small_coin, self.big_coin,
                         self.first_market, ask_price, self.second_market, bid_price, amount, trade_amount))
            return

        current_datetime = datetime.utcnow()
        current_datetime_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        first_market_trade_amount, second_market_trade_amount = self._first_buy_second_sell_pre_process(
            first_market_account=first_market_account, second_market_account=second_market_account,
            bid_price=bid_price, ask_price=ask_price, first_market_amount=trade_amount,
            second_market_amount=trade_amount
        )
        self._first_market_buy_second_market_sell_endpoint(self.first_market_symbol, first_market_trade_amount,
                                                           ask_price, self.second_market_symbol,
                                                           second_market_trade_amount, bid_price,
                                                           trade_target=TradeTarget.Hedge,
                                                           first_market_asks_depth=first_market_asks_depth,
                                                           second_market_bids_depth=second_market_bids_depth,
                                                           first_market_depth_time=first_market_depth_time,
                                                           second_market_depth_time=second_market_depth_time,
                                                           create_time=current_datetime)
        print("{}|WorthBuy|{}|{}|{}_ASKS|{}|{}_BIDS|{}|AMOUNT|{}|TradeAmount|{}".
              format(current_datetime_str, self.small_coin, self.big_coin, self.first_market,
                     ask_price, self.second_market, bid_price, amount, trade_amount))
        print("{}|AccountAfterBuy|{}|{}|{}|{}".
              format(current_datetime_str, self.first_market, first_market_account,
                     self.second_market, second_market_account))

    def first_market_sell_second_market_market_buy(self, first_market_account, second_market_account, bid_price,
                                                   ask_price, amount, first_market_bids_depth,
                                                   second_market_asks_depth, first_market_depth_time,
                                                   second_market_depth_time):
        """
        火币市场卖小币，币安市场买小币
        :param first_market_account:
        :param second_market_account:
        :param bid_price:
        :param ask_price:
        :param amount:
        :type amount: Decimal
        :param first_market_bids_depth: [(), ()]
        :param second_market_asks_depth [(), ()]
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        if self.depth_amount_check(amount) is False:
            print("{}|DepthAmountInvalid|{}|{}|{}_BIDS|{}|{}_ASKS|{}|AMOUNT|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self.small_coin, self.big_coin,
                         self.first_market, bid_price, self.second_market, ask_price, amount))
            return
        trade_amount = get_trade_amount(amount=amount)
        # 悲观做法，乘一个系数，避免币不够
        # 看看自己在第一个市场持有的小币够不够了
        if first_market_account[self.small_coin] < trade_amount / Decimal('0.95'):
            trade_amount = first_market_account[self.small_coin] * Decimal('0.95')
        # 看看自己在第二个市场持有的大币够不够买的
        if second_market_account[self.big_coin] < trade_amount * ask_price / Decimal('0.95'):
            trade_amount = second_market_account[self.big_coin] / ask_price * Decimal('0.95')
        # 交易量不够
        if self.trade_amount_check(trade_amount) is False:
            print("{}|TradeAmountInvalid|{}|{}|{}_BIDS|{}|{}_ASKS|{}|AMOUNT|{}|TRADEAMOUNT|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self.small_coin, self.big_coin,
                         self.first_market, bid_price, self.second_market, ask_price, amount, trade_amount))
            return
        first_market_trade_amount, second_market_trade_amount = self._first_sell_second_buy_pre_process(
            first_market_account=first_market_account, second_market_account=second_market_account,
            bid_price=bid_price, ask_price=ask_price, first_market_amount=trade_amount,
            second_market_amount=trade_amount
        )
        current_datetime = datetime.utcnow()
        current_datetime_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self._first_market_sell_second_market_buy_endpoint(self.first_market_symbol, first_market_trade_amount,
                                                           bid_price, self.second_market_symbol,
                                                           second_market_trade_amount, ask_price,
                                                           trade_target=TradeTarget.Hedge,
                                                           first_market_bids_depth=first_market_bids_depth,
                                                           second_market_asks_depth=second_market_asks_depth,
                                                           first_market_depth_time=first_market_depth_time,
                                                           second_market_depth_time=second_market_depth_time,
                                                           create_time=current_datetime)
        print("{}|WorthBuy|{}|{}|{}_BIDS|{}|{}_ASKS|{}|AMOUNT|{}|TradeAmount|{}".
              format(current_datetime_str, self.small_coin, self.big_coin,
                     self.first_market, bid_price, self.second_market, ask_price, amount, trade_amount))
        print("{}|AccountAfterBuy|{}|{}|{}|{}".
              format(current_datetime_str, self.first_market, first_market_account,
                     self.second_market, second_market_account))

    def first_market_small_coin_rebalance(self, first_market_account, second_market_account, second_market_bid_info,
                                          first_market_ask_info, small_point_amount, first_market_depth_time,
                                          second_market_depth_time):
        """
        first_market的coin数量太少了，再平衡，情况是first_market买，币安卖，传入的小币量必须是准确的，不考虑比特币不够的问题
        :param first_market_account:
        :param second_market_account:
        :param second_market_bid_info:
        :param first_market_ask_info:
        :param small_point_amount:
        :type small_point_amount: Decimal
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        if not second_market_bid_info or not first_market_ask_info:
            return
        second_market_bid_price = second_market_bid_info[0][0]
        first_market_ask_price = first_market_ask_info[0][0]
        # 在第二个市场卖的价低于在第一个市场买的价，亏损
        if second_market_bid_price < first_market_ask_price:
            return
        able_amount = get_trade_amount(min(second_market_bid_info[0][1], first_market_ask_info[0][1]))
        if first_market_account[self.small_coin] / small_point_amount > REBALANCE_THRESHOLD:  # 剩余超过10%
            return
        if self.trade_amount_check(able_amount) is False:
            print("{}|RebalanceAmountInvalid|{}|{}_BUY|{}_SELL".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), able_amount,
                         self.first_market, self.second_market))
            return
        first_market_buy_amount = small_point_amount / 2 - first_market_account[self.small_coin]
        # 存量不够用
        if first_market_buy_amount > able_amount:
            first_market_buy_amount = able_amount
        # 第二个市场卖的数量
        second_market_sell_amount = second_market_account[self.small_coin] - small_point_amount / 2
        if second_market_sell_amount < 0:  # 出现异常
            print("{}|RebalanceError|{}|{}_BUY|{}_SELL|{}_SMALL_COIN_SMALL_THAN_HALF|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), able_amount, self.first_market,
                         self.second_market, self.second_market, second_market_sell_amount))
            return
        if second_market_sell_amount > able_amount:
            second_market_sell_amount = able_amount
        first_market_trade_amount, second_market_trade_amount = self._first_buy_second_sell_pre_process(
            first_market_account=first_market_account, second_market_account=second_market_account,
            bid_price=second_market_bid_price, ask_price=first_market_ask_price,
            first_market_amount=first_market_buy_amount, second_market_amount=second_market_sell_amount)
        current_datetime = datetime.utcnow()
        current_datetime_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self._first_market_buy_second_market_sell_endpoint(self.first_market_symbol, first_market_trade_amount,
                                                           first_market_ask_price, self.second_market_symbol,
                                                           second_market_trade_amount, second_market_bid_price,
                                                           trade_target=TradeTarget.ReBalance,
                                                           first_market_asks_depth=first_market_ask_info,
                                                           second_market_bids_depth=second_market_bid_info,
                                                           first_market_depth_time=first_market_depth_time,
                                                           second_market_depth_time=second_market_depth_time,
                                                           create_time=current_datetime)
        print("{}|Rebalance|{}|{}|{}_BUY|{}|{}_SELL|{}|{}_AMOUNT|{}|{}_AMOUNT|{}".
              format(current_datetime_str, self.small_coin, self.big_coin, self.first_market,
                     first_market_ask_price, self.second_market,  second_market_bid_price, self.first_market,
                     first_market_trade_amount, self.second_market, second_market_trade_amount))
        print("{}|AccountAfterBuy|{}|{}|{}|{}".
              format(current_datetime_str, self.first_market, first_market_account,
                     self.second_market, second_market_account))

    def second_market_small_coin_rebalance(self, first_market_account, second_market_account, first_market_bid_info,
                                           second_market_ask_info, small_point_amount, first_market_depth_time,
                                           second_market_depth_time):
        """
        second_market的小coin数量太少了，再平衡，情况是second_market买，火币卖，传入的小币量必须是准确的，不考虑比特币不够的问题
        :param first_market_account:
        :param second_market_account:
        :param first_market_bid_info:
        :param second_market_ask_info:
        :param small_point_amount:
        :type small_point_amount: Decimal
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        if not first_market_bid_info or not second_market_ask_info:
            return
        first_market_bid_price = first_market_bid_info[0][0]
        second_market_ask_price = second_market_ask_info[0][0]
        # 在第一个市场的卖价低于在第二个市场的买价，亏损
        if first_market_bid_price < second_market_ask_price:
            return
        able_amount = get_trade_amount(min(first_market_bid_info[0][1], second_market_ask_info[0][1]))
        if second_market_account[self.small_coin] / small_point_amount > REBALANCE_THRESHOLD:  # 剩余超过10%
            return
        if self.trade_amount_check(able_amount) is False:
            print("{}|RebalanceAmountInvalid|{}|{}_SELL|{}_BUY".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), able_amount,
                         self.first_market, self.second_market))
            return
        second_market_buy_amount = small_point_amount / 2 - second_market_account[self.small_coin]
        # 存量不够用
        if second_market_buy_amount > able_amount:
            second_market_buy_amount = able_amount
        # 第一个市场卖的数量
        first_market_sell_amount = first_market_account[self.small_coin] - small_point_amount / 2
        if first_market_sell_amount < 0:  # 出现异常
            print("{}|RebalanceError|{}|{}_SELL|{}_BUY|{}_SMALL_COIN_SMALL_THAN_HALF|{}".
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), able_amount, self.first_market,
                         self.second_market, self.first_market, first_market_sell_amount))
            return
        if first_market_sell_amount > able_amount:
            first_market_sell_amount = able_amount
        first_market_trade_amount, second_market_trade_amount = self._first_sell_second_buy_pre_process(
            first_market_account=first_market_account, second_market_account=second_market_account,
            bid_price=first_market_bid_price, ask_price=second_market_ask_price,
            first_market_amount=first_market_sell_amount, second_market_amount=second_market_buy_amount)
        current_datetime = datetime.utcnow()
        current_datetime_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self._first_market_sell_second_market_buy_endpoint(self.first_market_symbol, first_market_trade_amount,
                                                           first_market_bid_price,
                                                           self.second_market_symbol, second_market_trade_amount,
                                                           second_market_ask_price, trade_target=TradeTarget.ReBalance,
                                                           first_market_bids_depth=first_market_bid_info,
                                                           second_market_asks_depth=second_market_ask_info,
                                                           first_market_depth_time=first_market_depth_time,
                                                           second_market_depth_time=second_market_depth_time,
                                                           create_time=current_datetime)
        print("{}|Rebalance|{}|{}|{}_BUY|{}|{}_SELL|{}|{}_AMOUNT|{}|{}_AMOUNT|{}".
              format(current_datetime_str, self.small_coin, self.big_coin, self.first_market,
                     first_market_bid_price, self.second_market,  second_market_ask_price,
                     self.first_market, first_market_trade_amount, self.second_market,
                     second_market_trade_amount))
        print("{}|AccountAfterBuy|{}|{}|{}|{}".
              format(current_datetime_str, self.first_market, first_market_account,
                     self.second_market, second_market_account))

    def small_coin_adjust(self, first_market_account, second_market_account, small_coin_amount,
                          first_market_depth_info, second_market_depth_info, first_market_depth_time,
                          second_market_depth_time):
        """
        是否需要补充/卖出小币
        :param first_market_account:
        :param second_market_account:
        :param small_coin_amount: 单个市场初始小币数量
        :param first_market_depth_info:
        :param second_market_depth_info:
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        # 火币中，frozen指的是还没有进行换算到其它币的数额，币安未知
        first_market_small_total = first_market_account[self.small_coin]
        second_market_small_total = second_market_account[self.small_coin]
        small_total = first_market_small_total + second_market_small_total
        current_datetime = datetime.utcnow()
        current_datetime_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        # 整体是否少了
        if small_total < small_coin_amount * SMALL_COIN_SUPPLEMENT_LOW_THRESHOLD:
            need_buy_amount = small_coin_amount - small_total
            if first_market_small_total < second_market_small_total:  # 第一个市场买
                trade_pair_id = '{}_{}'.format(int(time.time()*1000), '{}_MARKET_BUY'.format(self.first_market))
                trade_price = self.find_trade_price(need_buy_amount, first_market_depth_info['asks'])
                trade_amount = need_buy_amount
                # 大币够不够用
                if first_market_account[self.big_coin] * Decimal('0.95') < trade_amount:
                    trade_amount = first_market_account[self.big_coin] * Decimal('0.95')
                first_market_buy_amount = self._first_buy_pre_process(first_market_account=first_market_account,
                                                                      ask_price=trade_price,
                                                                      first_market_amount=trade_amount)
                self._first_market_buy(trade_pair_id=trade_pair_id, symbol=self.first_market_symbol,
                                       amount=first_market_buy_amount, price=trade_price,
                                       trade_target=TradeTarget.SmallCoinAdjust,
                                       first_market_asks_depth=first_market_depth_info['asks'],
                                       depth_time=first_market_depth_time,
                                       create_time=current_datetime)
                print("{}|SmallCoinAdjust|{}|{}|NEED_BUY|{}|{}_BUY|{}|{}_AMOUNT|{}".
                      format(current_datetime_str, self.small_coin, self.big_coin, need_buy_amount,
                             self.first_market, first_market_buy_amount, self.first_market, trade_price))
                print("{}|AccountAfterBuy|{}|{}|{}|{}".
                      format(current_datetime_str, self.first_market, first_market_account,
                             self.second_market, second_market_account))
            else:  # 第二个市场买
                trade_pair_id = '{}_{}'.format(int(time.time()*1000), '{}_MARKET_BUY'.format(self.second_market))
                trade_price = self.find_trade_price(need_buy_amount, second_market_depth_info['asks'])
                trade_amount = need_buy_amount
                # 大币够不够用
                if second_market_account[self.big_coin] * Decimal('0.95') < trade_amount * trade_price:
                    trade_amount = second_market_account[self.big_coin] * Decimal('0.95') / trade_price
                second_market_buy_amount = self._second_buy_pre_process(second_market_account=second_market_account,
                                                                        ask_price=trade_price,
                                                                        second_market_amount=trade_amount)
                self._second_market_buy(trade_pair_id=trade_pair_id, symbol=self.second_market_symbol,
                                        amount=second_market_buy_amount, price=trade_price,
                                        trade_target=TradeTarget.SmallCoinAdjust,
                                        second_market_asks_depth=second_market_depth_info['asks'],
                                        depth_time=second_market_depth_time, create_time=current_datetime)
                print("{}|SmallCoinAdjust|{}|{}|NEED_BUY|{}|{}_BUY|{}|{}_AMOUNT|{}".
                      format(current_datetime_str, self.small_coin, self.big_coin, need_buy_amount,
                             self.second_market, second_market_buy_amount, self.second_market, trade_price))
                print("{}|AccountAfterBuy|{}|{}|{}|{}".
                      format(current_datetime_str, self.first_market, first_market_account,
                             self.second_market, second_market_account))
        elif small_total > small_coin_amount * SMALL_COIN_SUPPLEMENT_HIGH_THRESHOLD:  # 整体小币太多了
            need_sell_amount = small_total - small_coin_amount
            if first_market_small_total > second_market_small_total:  # 第一个市场卖
                trade_pair_id = '{}_{}'.format(int(time.time()*1000), '{}_MARKET_SELL'.format(self.first_market))
                trade_price = self.find_trade_price(need_sell_amount, first_market_depth_info['bids'])
                trade_amount = need_sell_amount
                # 小币够不够用
                if first_market_account[self.small_coin] * Decimal('0.95') < trade_amount:
                    trade_amount = first_market_account[self.small_coin] * Decimal('0.95')
                first_market_sell_amount = self._first_sell_pre_process(first_market_account=first_market_account,
                                                                        bid_price=trade_price,
                                                                        first_market_amount=trade_amount)
                self._first_market_sell(trade_pair_id=trade_pair_id, symbol=self.first_market_symbol,
                                        amount=first_market_sell_amount, price=trade_price,
                                        trade_target=TradeTarget.SmallCoinAdjust,
                                        first_market_bids_depth=first_market_depth_info['bids'],
                                        depth_time=first_market_depth_time,
                                        create_time=current_datetime)
                print("{}|SmallCoinAdjust|{}|{}|NEED_SELL|{}|{}_SELL|{}|{}_AMOUNT|{}".
                      format(current_datetime_str, self.small_coin, self.big_coin, need_sell_amount,
                             self.first_market, first_market_sell_amount, self.first_market, trade_price))
                print("{}|AccountAfterBuy|{}|{}|{}|{}".
                      format(current_datetime_str, self.first_market, first_market_account,
                             self.second_market, second_market_account))
            else:  # 第二个市场卖
                trade_pair_id = '{}_{}'.format(int(time.time()*1000), '{}_MARKET_SELL'.format(self.second_market))
                trade_price = self.find_trade_price(need_sell_amount, second_market_depth_info['bids'])
                trade_amount = need_sell_amount
                # 小币够不够用
                if second_market_account[self.small_coin] * Decimal('0.95') < trade_amount:
                    trade_amount = second_market_account[self.small_coin] * Decimal('0.95')
                second_market_trade_amount = self._second_sell_pre_process(second_market_account=second_market_account,
                                                                           bid_price=trade_price,
                                                                           second_market_amount=trade_amount)
                self._second_market_sell(trade_pair_id=trade_pair_id, symbol=self.second_market_symbol,
                                         amount=second_market_trade_amount, price=trade_price,
                                         trade_target=TradeTarget.SmallCoinAdjust,
                                         second_market_bids_depth=second_market_depth_info['bids'],
                                         depth_time=second_market_depth_time, create_time=current_datetime)
                print("{}|SmallCoinAdjust|{}|{}|NEED_SELL|{}|{}_SELL|{}|{}_AMOUNT|{}".
                      format(current_datetime_str, self.small_coin, self.big_coin, need_sell_amount,
                             self.second_market, second_market_trade_amount, self.second_market, trade_price))
                print("{}|AccountAfterBuy|{}|{}|{}|{}".
                      format(current_datetime_str, self.first_market, first_market_account,
                             self.second_market, second_market_account))
