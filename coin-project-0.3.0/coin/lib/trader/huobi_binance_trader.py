# -*- coding=utf-8 -*-
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
import time
from coin.lib.config import REBALANCE_THRESHOLD, SMALL_COIN_SUPPLEMENT_LOW_THRESHOLD, \
    SMALL_COIN_SUPPLEMENT_HIGH_THRESHOLD, PRECISE
from coin.lib.trader.trader_base import TraderBase
from coin.lib.utils import TradeTarget, get_trade_amount, Market, TradeSide, OrderType


class HuobiBinanceTrader(TraderBase):

    __trade_pair__ = None  # 形式为小币_大币

    def __init__(self, combination, huobi_trade_api, binance_trader_api, small_coin,
                 big_coin, huobi_symbol, binance_symbol,
                 trade_amount_threshold):
        super(HuobiBinanceTrader, self).__init__(combination=combination, first_trade_api=huobi_trade_api,
                                                 second_trader_api=binance_trader_api,
                                                 first_market=Market.HUOBI, second_market=Market.BINANCE,
                                                 small_coin=small_coin, big_coin=big_coin,
                                                 first_market_symbol=huobi_symbol, second_market_symbol=binance_symbol,
                                                 trade_amount_threshold=trade_amount_threshold)

    def _first_market_send_buy_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        amount_str = str(amount)
        return self.first_trade_api.place_order(symbol=symbol, order_type=OrderType.BuyMarket,
                                                amount=amount_str)

    def _first_market_send_sell_request(self, symbol, order_type, amount):
        """
        第一个市场发送买的请求
        :param symbol:
        :param order_type:
        :param amount:
        :return: order_id
        """
        amount_str = str(amount)
        return self.first_trade_api.place_order(symbol=symbol, order_type=OrderType.SellMarket,
                                                amount=amount_str)

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


class HuobiBinanceIOSTBTCTrader(HuobiBinanceTrader):

    __trade_pair__ = 'iost_btc'

    def __init__(self, combination, huobi_trade_api, binance_trader_api):
        super(HuobiBinanceIOSTBTCTrader, self).__init__(combination=combination,
                                                        huobi_trade_api=huobi_trade_api,
                                                        binance_trader_api=binance_trader_api,
                                                        small_coin='iost',
                                                        big_coin='btc',
                                                        huobi_symbol='iostbtc',
                                                        binance_symbol='IOSTBTC',
                                                        trade_amount_threshold=200)


class HuobiBinanceTRXETHTrader(HuobiBinanceTrader):

    __trade_pair__ = 'trx_eth'

    def __init__(self, combination, huobi_trade_api, binance_trader_api):
        super(HuobiBinanceTRXETHTrader, self).__init__(combination=combination,
                                                       huobi_trade_api=huobi_trade_api,
                                                       binance_trader_api=binance_trader_api,
                                                       small_coin='trx',
                                                       big_coin='eth',
                                                       huobi_symbol='trxeth',
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
        if amount > 10000:
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
        if amount > 10000:
            return False
        return True


class HuobiBinanceDGDETHTrader(HuobiBinanceTrader):

    __trade_pair__ = 'dgd_eth'

    def __init__(self, combination, huobi_trade_api, binance_trader_api):
        super(HuobiBinanceDGDETHTrader, self).__init__(combination=combination,
                                                       huobi_trade_api=huobi_trade_api,
                                                       binance_trader_api=binance_trader_api,
                                                       small_coin='dgd',
                                                       big_coin='eth',
                                                       huobi_symbol='dgdeth',
                                                       binance_symbol='DGDETH',
                                                       trade_amount_threshold=0.002)


class HuobiBinanceKNCBTCTrader(HuobiBinanceTrader):

    __trade_pair__ = 'knc_btc'

    def __init__(self, combination, huobi_trade_api, binance_trader_api):
        super(HuobiBinanceKNCBTCTrader, self).__init__(combination=combination,
                                                       huobi_trade_api=huobi_trade_api,
                                                       binance_trader_api=binance_trader_api,
                                                       small_coin='knc',
                                                       big_coin='btc',
                                                       huobi_symbol='kncbtc',
                                                       binance_symbol='KNCBTC',
                                                       trade_amount_threshold=20)


class HuobiBinanceENGBTCTrader(HuobiBinanceTrader):

    __trade_pair__ = 'eng_btc'

    def __init__(self, combination, huobi_trade_api, binance_trader_api):
        super(HuobiBinanceENGBTCTrader, self).__init__(combination=combination,
                                                       huobi_trade_api=huobi_trade_api,
                                                       binance_trader_api=binance_trader_api,
                                                       small_coin='eng',
                                                       big_coin='btc',
                                                       huobi_symbol='engbtc',
                                                       binance_symbol='ENGBTC',
                                                       trade_amount_threshold=2)
