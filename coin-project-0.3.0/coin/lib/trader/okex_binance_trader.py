# -*- coding=utf-8 -*-
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from coin.lib.trader.trader_base import TraderBase
from coin.lib.utils import Market, OrderType


class OKExBinanceTrader(TraderBase):

    __trade_pair__ = None  # 形式为小币_大币

    def __init__(self, combination, okex_trade_api, binance_trader_api, small_coin,
                 big_coin, okex_symbol, binance_symbol,
                 trade_amount_threshold):
        super(OKExBinanceTrader, self).__init__(combination=combination, first_trade_api=okex_trade_api,
                                                second_trader_api=binance_trader_api,
                                                first_market=Market.OKEX, second_market=Market.BINANCE,
                                                small_coin=small_coin, big_coin=big_coin,
                                                first_market_symbol=okex_symbol, second_market_symbol=binance_symbol,
                                                trade_amount_threshold=trade_amount_threshold)

    def _first_market_send_buy_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        return self.first_trade_api.market_buy(symbol=symbol, amount=amount)

    def _first_market_send_sell_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        return self.first_trade_api.market_sell(symbol=symbol, amount=amount)

    def _second_market_send_buy_request(self, symbol, order_type, amount):
        """
        第二个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        res = self.second_trader_api.order_market_buy(symbol=symbol, quantity=amount)
        return res['orderId']

    def _second_market_send_sell_request(self, symbol, order_type, amount):
        """
        第二个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        res = self.second_trader_api.order_market_sell(symbol=symbol, quantity=amount)
        return res['orderId']

    def _first_sell_pre_process(self, first_market_account, bid_price, first_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量，并修改account
        :param first_market_account:
        :param bid_price:
        :param first_market_amount:
        :return:
        """
        first_market_trade_amount = first_market_amount. \
            quantize(Decimal(self.first_market_sell_precise), rounding=ROUND_DOWN)
        first_market_account[self.big_coin] += first_market_trade_amount * bid_price
        first_market_account[self.small_coin] -= first_market_trade_amount
        return first_market_trade_amount

    def _first_buy_pre_process(self, first_market_account, ask_price, first_market_amount):
        """
        预处理，得到实际作为交易参数的第一个市场的交易数量，并修改account
        :param first_market_account:
        :param ask_price:
        :param first_market_amount:
        :return: first_market_trade_amount
        """
        first_market_trade_amount = first_market_amount * ask_price
        first_market_trade_amount = first_market_trade_amount.quantize(Decimal(self.first_market_buy_precise),
                                                                       rounding=ROUND_DOWN)
        # 修改Account数量
        first_market_account[self.big_coin] -= first_market_trade_amount
        first_market_account[self.small_coin] += first_market_trade_amount / ask_price
        return first_market_trade_amount

    def _second_sell_pre_process(self, second_market_account, bid_price, second_market_amount):
        """
        预处理，得到实际作为交易参数的第二个市场的交易数量，并修改account
        :param second_market_account:
        :param bid_price:
        :param second_market_amount:
        :return:
        """
        second_market_trade_amount = second_market_amount.quantize(Decimal(self.second_market_sell_precise),
                                                                   rounding=ROUND_DOWN)
        second_market_account[self.big_coin] += second_market_trade_amount * bid_price
        second_market_account[self.small_coin] -= second_market_trade_amount
        return second_market_trade_amount

    def _second_buy_pre_process(self, second_market_account, ask_price, second_market_amount):
        """
        预处理，得到实际作为交易参数的第二个市场的交易数量，并修改account
        :param second_market_account:
        :param ask_price:
        :return:
        """
        second_market_trade_amount = second_market_amount. \
            quantize(Decimal(self.second_market_buy_precise), rounding=ROUND_DOWN)
        second_market_account[self.big_coin] -= second_market_trade_amount * ask_price
        second_market_account[self.small_coin] += second_market_trade_amount
        return second_market_trade_amount

    def bnb_supplement(self, amount):
        """
        补充bnb
        :param amount:
        :return:
        """
        symbol = 'BNB{}'.format(self.big_coin).upper()
        current_datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        self._second_market_send_buy_request(symbol=symbol, amount=amount,
                                             order_type=OrderType.BuyMarket)
        print("{}|BNBSupplement|{}|".format(current_datetime_str, amount))

    def first_market_small_coin_rebalance(self, first_market_account, second_market_account, second_market_bid_info,
                                          first_market_ask_info, small_point_amount, first_market_depth_time,
                                          second_market_depth_time):
        """
        okex没有再平衡
        :param first_market_account:
        :param second_market_account:
        :param second_market_bid_info:
        :param first_market_ask_info:
        :param small_point_amount:
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        return

    def second_market_small_coin_rebalance(self, first_market_account, second_market_account, first_market_bid_info,
                                           second_market_ask_info, small_point_amount, first_market_depth_time,
                                           second_market_depth_time):
        """
        okex没有再平衡
        :param first_market_account:
        :param second_market_account:
        :param first_market_bid_info:
        :param second_market_ask_info:
        :param small_point_amount:
        :param first_market_depth_time:
        :param second_market_depth_time:
        :return:
        """
        return


class OKExBinanceIOSTBTCTrader(OKExBinanceTrader):

    __trade_pair__ = 'iost_btc'

    def __init__(self, combination, okex_trade_api, binance_trader_api):
        super(OKExBinanceIOSTBTCTrader, self).__init__(combination=combination,
                                                       okex_trade_api=okex_trade_api,
                                                       binance_trader_api=binance_trader_api,
                                                       small_coin='iost',
                                                       big_coin='btc',
                                                       okex_symbol='iost_btc',
                                                       binance_symbol='IOSTBTC',
                                                       trade_amount_threshold=200)


class OKExBinanceTRXETHTrader(OKExBinanceTrader):

    __trade_pair__ = 'trx_eth'

    def __init__(self, combination, okex_trade_api, binance_trader_api):
        super(OKExBinanceTRXETHTrader, self).__init__(combination=combination,
                                                      okex_trade_api=okex_trade_api,
                                                      binance_trader_api=binance_trader_api,
                                                      small_coin='trx',
                                                      big_coin='eth',
                                                      okex_symbol='trx_eth',
                                                      binance_symbol='TRXETH',
                                                      trade_amount_threshold=20)

    def depth_amount_check(self, amount):
        """
        从深度信息获取的amount检查
        :param amount: 深度信息读取出来允许进行多少交易
        :return:
        """
        if amount < self.trade_amount_threshold:
            return False
        if amount > 20000:
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
        if amount > 20000:
            return False
        return True


class OKExBinanceNEOETHTrader(OKExBinanceTrader):

    __trade_pair__ = 'neo_eth'

    def __init__(self, combination, okex_trade_api, binance_trader_api):
        super(OKExBinanceNEOETHTrader, self).__init__(combination=combination,
                                                      okex_trade_api=okex_trade_api,
                                                      binance_trader_api=binance_trader_api,
                                                      small_coin='neo',
                                                      big_coin='eth',
                                                      okex_symbol='neo_eth',
                                                      binance_symbol='NEOETH',
                                                      trade_amount_threshold=0.02)
