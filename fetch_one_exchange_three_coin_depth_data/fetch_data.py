# author: ouyan
# date: 2018-03-10
# comment: fetch two exchange depth data

import conn
import time
import util
import config
import json
import os
from datetime import datetime

# init setup
binance_client = conn.BinanceClient()
huobi_client = conn.HuobiClient()
mysql_client = conn.MySQLClient()
mysql_client.connect()
exchange_client_dict = {'huobi' : huobi_client, 'binance' : binance_client}
exchange_symbols = config.exchange_symbols

# get data and export to mysql database
while 1:
        for exchange_symbol in exchange_symbols:
                ts = int(round(time.time()))
		dt = datetime.utcfromtimestamp(ts)
		log_time = dt.strftime('%Y-%m-%d %H:%M:%S')
		exchange = exchange_symbol[0]
                symbol1 = exchange_symbol[1]
		symbol2 = exchange_symbol[2]
		symbol3 = exchange_symbol[3]
		symbol = symbol1 + '|' + symbol2 + '|' + symbol3
                symbol1 = util.symbol_transform(symbol1, exchange)
		symbol2 = util.symbol_transform(symbol2, exchange)
		symbol3 = util.symbol_transform(symbol3, exchange)
		symbol1_bids, symbol1_asks = exchange_client_dict[exchange].get_depth_data(symbol1)
                symbol2_bids, symbol2_asks = exchange_client_dict[exchange].get_depth_data(symbol2)
                symbol3_bids, symbol3_asks = exchange_client_dict[exchange].get_depth_data(symbol3)
                mysql_client.insert_depth_data(log_time, symbol, exchange, json.dumps(symbol1_bids), json.dumps(symbol1_asks), json.dumps(symbol2_bids), json.dumps(symbol2_asks), json.dumps(symbol3_bids), json.dumps(symbol3_asks))
	time.sleep(1)

# close connection
mysql_client.disconnect()
