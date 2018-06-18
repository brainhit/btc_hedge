import MySQLdb
import json
import util

# init setup
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_analysis'

# fetch data
# ['binance/huobi', 'iost/btc'],
# ['binance/huobi', 'eth/btc'],
# ['binance/huobi', 'ltc/btc'],
# ['binance/huobi', 'neo/btc'],
# ['binance/huobi', 'mco/btc'],
# ['binance/huobi', 'mtl/btc'],
# ['binance/huobi', 'eos/btc'],
# ['binance/huobi', 'trx/btc'],
# ['binance/huobi', 'xrp/btc'],
# ['binance/huobi', 'ven/btc'],
# ['binance/huobi', 'icx/btc'],
# ['binance/huobi', 'zil/btc'],
# ['binance/huobi', 'ont/btc'],
exchange_pair = 'binance/huobi'
small_coin = 'eos'
big_coin = 'btc'
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select * from two_exchange_hedge_depth where exchange_pair='{}' and symbol='{}/{}' and substring(log_date, 1, 10)>='2018-03-17' order by log_date desc".format(exchange_pair, small_coin, big_coin)
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

hedge_data_clean = []
hedge_data_clean.append(hedge_data[0]); amo = hedge_data[0][-1]
for i in range(1, len(hedge_data)):
	if hedge_data[i][-1] == amo: continue
	else:
		amo = hedge_data[i][-1];
		hedge_data_clean.append(hedge_data[i])

count = 0
for i in hedge_data_clean:
	if i[1] != 0: count += 1; print(i)
print(count)

# close connection
conn.close()
