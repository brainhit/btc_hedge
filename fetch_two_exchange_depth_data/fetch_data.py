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
hitbtc_client = conn.HITBTCClient()
bittrex_client = conn.BITTREXClient()
mysql_client = conn.MySQLClient()
mysql_client.connect()
exchange_client_dict = {'huobi' : huobi_client, 'binance' : binance_client, 'okex' : okex_client, 'hitbtc' : hitbtc_client, 'bittrex': bittrex_client}
exchange_pairs_symbols = config.exchange_pairs_symbols

# get data and export to mysql database
while 1:
        for exchange_pair_symbol in exchange_pairs_symbols:
                ts = int(round(time.time()))
		dt = datetime.utcfromtimestamp(ts)
		log_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                exchange_pair = exchange_pair_symbol[0]
                symbol = exchange_pair_symbol[1]
                exchange1 = exchange_pair.split('/')[0]
                exchange2 = exchange_pair.split('/')[1]
                exchange1_symbol = util.symbol_transform(symbol, exchange1)
                exchange2_symbol = util.symbol_transform(symbol, exchange2)
                exchange1_bids, exchange1_asks = exchange_client_dict[exchange1].get_depth_data(exchange1_symbol)
                exchange2_bids, exchange2_asks = exchange_client_dict[exchange2].get_depth_data(exchange2_symbol)
                mysql_client.insert_depth_data(log_date, symbol, exchange_pair, json.dumps(exchange1_bids), json.dumps(exchange1_asks), json.dumps(exchange2_bids), json.dumps(exchange2_asks))

# close connection
mysql_client.disconnect()
