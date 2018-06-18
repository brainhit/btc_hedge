import MySQLdb
import json
import util
import sys
import config

# init setup
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_analysis'
day = sys.argv[1]
exchange_pairs_symbols = config.exchange_pairs_symbols

for exchange_pair_symbol in exchange_pairs_symbols:
	exchange_pair = exchange_pair_symbol[0]
	small_coin = exchange_pair_symbol[1].split('/')[0]
	big_coin = exchange_pair_symbol[1].split('/')[1]

	# fetch data
	conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
	cur = conn.cursor()
	sql = "select * from two_exchange_hedge_depth where exchange_pair='{}' and symbol='{}/{}' and substring(log_date, 1, 10)='{}' order by log_date desc".format(exchange_pair, small_coin, big_coin, day)
	cur.execute(sql)
	res = []
	for row in cur.fetchall():
		res.append([row[0], json.loads(row[3]), json.loads(row[4]), json.loads(row[5]), json.loads(row[6])])

	# analyze data
	hedge_data = []
	for i in range(0, len(res)):
		data = res[i]
		log_date = data[0]
		flag = 0; bid = 0; ask = 0; amo = 0
		if not data[1] or not data[2] or not data[3] or not data[4]:
			continue
		bid_price, ask_price, amount = util.find_profit(data[1], data[4])
		if amount != 0: # huobi buy binance sell
			bid = bid_price; ask = ask_price; amo = amount; flag = 1
		bid_price, ask_price, amount = util.find_profit(data[3], data[2])
		if amount != 0: # huobi sell binance buy
			bid = bid_price; ask = ask_price; amo = amount; flag = -1
		hedge_data.append([log_date, flag, bid, ask, amo])

	if len(hedge_data) == 0: continue

	hedge_data_clean = []
	hedge_data_clean.append(hedge_data[0]); amo = hedge_data[0][-1]
	for i in range(1, len(hedge_data)):
		if hedge_data[i][-1] == amo: continue
		else:
			amo = hedge_data[i][-1];
			hedge_data_clean.append(hedge_data[i])

	count = 0
	neg = 0
	pos = 0
	for i in hedge_data_clean:
		if i[1] != 0: count += 1
		if i[1] == 1: pos += 1
		if i[1] == -1: neg += 1

	# write data to mysql database
	sql = "insert into combination_opt (exchange_pair, symbol, opt_num, opt_pos_num, opt_neg_num, log_date) values ('{}', '{}', {}, {}, {}, '{}')".format(exchange_pair, small_coin + '/' + big_coin, count, pos, neg, day)
	cur.execute(sql)
	conn.commit()

# close connection
conn.close()
