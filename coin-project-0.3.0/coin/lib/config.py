# -*- coding=utf-8 -*-
from decimal import Decimal

# 测试用

# DB = 'btc_trade_test'  # 测试用
# AES_KEY = 'xxxx'


# 线上用
DB = 'btc_trade'  # 线上用
AES_KEY = 'xxxx'


# 公用
TIMEOUT = 5  # 秒
# HUOBI_BOOK_TIMEOUT = 0.5  # 订单数据过期时间
# BINANCE_BOOK_TIMEOUT = 0.5  # 订单数据过期时间
BOOK_TIMEOUT = 0.5
TRADE_THRESHOLD = Decimal('0.003')
RECONNECT_TIME = 36000  # 重新连接时间，单位秒
MARKET_URL = TRADE_URL = "https://api.huobi.pro"
low_greedy_coefficient = Decimal('0.25')  # 贪心系数，低于10万我们应该买能够获利的多少数量
high_greedy_coefficient = Decimal('0.3')  # 贪心系数，超过10万
REBALANCE_THRESHOLD = Decimal('0.05')  # 整体小币的百分比
SMALL_COIN_SUPPLEMENT_LOW_THRESHOLD = Decimal('0.98')
SMALL_COIN_SUPPLEMENT_HIGH_THRESHOLD = Decimal('1.02')
# 补充bnb阈值
BNB_SUPPLEMENT_THRESHOLD = Decimal('1')
BNB_SUPPLEMENT = Decimal('1')

PRECISE = {
    'BINANCE': {
        'iost_btc': {
            'BUY': '1',
            'SELL': '1',
        },
        'trx_eth': {
            'BUY': '1',
            'SELL': '1',
        },
        'knc_btc': {
            'BUY': '1',
            'SELL': '1',
        },
        'dgd_eth': {
            'BUY': '0.001',
            'SELL': '0.001',
        },
        'neo_eth': {
            'BUY': '0.01',
            'SELL': '0.01',
        },
        'eng_btc': {
            'BUY': '1',
            'SELL': '1',
        }
    },
    'HUOBI': {
        'iost_btc': {
            'BUY': '0.00000001',
            'SELL': '0.01'
        },
        'trx_eth': {
            'BUY': '0.00000001',
            'SELL': '0.01'
        },
        'knc_btc': {
            'BUY': '0.00000001',
            'SELL': '1'
        },
        'dgd_eth': {
            'BUY': '0.00000001',
            'SELL': '0.0001',
        },
        'xrp_btc': {
            'BUY': '0.00000001',
            'SELL': '1',
        },
        'eng_btc': {
            'BUY': '0.00000001',
            'SELL': '0.01'
        }
    },
    'OKEX': {
        'iost_btc': {
            'BUY': '0.00000001',
            'SELL': '0.01'
        },
        'trx_eth': {
            'BUY': '0.00000001',
            'SELL': '0.01'
        },
        'dgd_eth': {
            'BUY': '0.00000001',
            'SELL': '0.0001',
        },
        'neo_eth': {
            'BUY': '0.00000001',
            'SELL': '0.0001',
        },
        'xrp_btc': {
            'BUY': '0.00000001',
            'SELL': '0.01',
        }
    }
}

SQL_USER = 'taohuashan'
SQL_PSW = '123@admin'
