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
huobi_client = conn.HuobiClient()
binance_client = conn.BinanceClient()
okex_client = conn.OKEXClient()
mysql_client = conn.MySQLClient()
mysql_client.connect()
exchange_client_dict = {'okex' : okex_client, 'huobi' : huobi_client, 'binance' : binance_client}
exchange_pairs_symbols = config.exchange_pairs_symbols

# get data and export to mysql database
while 1:
        for exchange_pair_symbol in exchange_pairs_symbols:
                ts = int(round(time.time()))
		dt = datetime.utcfromtimestamp(ts)
		log_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                exchange_pair = exchange_pair_symbol[0]
                symbol1 = exchange_pair_symbol[1]
		symbol2 = exchange_pair_symbol[2]
		symbol = symbol1 + '|' + symbol2
                exchange1 = exchange_pair.split('/')[0]
                exchange2 = exchange_pair.split('/')[1]
                exchange1_symbol1 = util.symbol_transform(symbol1, exchange1)
		exchange1_symbol2 = util.symbol_transform(symbol2, exchange1)
                exchange2_symbol1 = util.symbol_transform(symbol1, exchange2)
                exchange2_symbol2 = util.symbol_transform(symbol2, exchange2)
                exchange1_symbol1_bids, exchange1_symbol1_asks = exchange_client_dict[exchange1].get_depth_data(exchange1_symbol1)
                exchange2_symbol1_bids, exchange2_symbol1_asks = exchange_client_dict[exchange2].get_depth_data(exchange2_symbol1)
                exchange1_symbol2_bids, exchange1_symbol2_asks = exchange_client_dict[exchange1].get_depth_data(exchange1_symbol2)
                exchange2_symbol2_bids, exchange2_symbol2_asks = exchange_client_dict[exchange2].get_depth_data(exchange2_symbol2)
                mysql_client.insert_depth_data(log_date, symbol, exchange_pair, json.dumps(exchange1_symbol1_bids), json.dumps(exchange1_symbol1_asks), json.dumps(exchange1_symbol2_bids), json.dumps(exchange1_symbol2_asks), json.dumps(exchange2_symbol1_bids), json.dumps(exchange2_symbol1_asks), json.dumps(exchange2_symbol2_bids), json.dumps(exchange2_symbol2_asks))

# close connection
mysql_client.disconnect()
