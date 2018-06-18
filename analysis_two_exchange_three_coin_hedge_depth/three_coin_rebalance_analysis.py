import MySQLdb
import json
import util

# init setup
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_analysis'

# fetch data
exchange_pair = 'binance/okex'
small_coin = 'iost'
big_coin1 = 'btc'
big_coin2 = 'eth'
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select * from two_exchange_three_coin_hedge_depth where exchange_pair='{}' and symbol='{}/{}|{}/{}' order by log_date desc".format(exchange_pair, small_coin, big_coin1, small_coin, big_coin2)
cur.execute(sql)
res = []
for row in cur.fetchall():
	res.append([row[0], json.loads(row[3]), json.loads(row[4]), json.loads(row[5]), json.loads(row[6]), json.loads(row[7]), json.loads(row[8]), json.loads(row[9]), json.loads(row[10])])

# analyze data
hedge_data = []
for i in range(0, len(res)):
	data = res[i][:]
	log_date = data[0]
	flag_sym1 = 0
	flag_sym2 = 0
	bid_price_sym1 = 0
	ask_price_sym1 = 0
	amount_sym1 = 0
	bid_price_sym2 = 0
	ask_price_sym2 = 0
	amount_sym2 = 0
	if not data[1] or not data[2] or not data[3] or not data[4] or not data[5] or not data[6] or not data[7] or not data[8]:
		continue
	bid_price, ask_price, amount = util.find_profit(data[1], data[6])
	if amount != 0: # huobi buy binance sell
		bid_price_sym1 = bid_price; ask_price_sym1 = ask_price
		amount_sym1 = amount; flag_sym1 = 1
        bid_price, ask_price, amount = util.find_profit(data[5], data[2])
	if amount != 0: # huobi sell binance buy
		bid_price_sym1 = bid_price; ask_price_sym1 = ask_price
                amount_sym1 = amount; flag_sym1 = -1
        bid_price, ask_price, amount = util.find_profit(data[3], data[8])
	if amount != 0: # huobi buy binance sell
		bid_price_sym2 = bid_price; ask_price_sym2 = ask_price
		amount_sym2 = amount; flag_sym2 = 1
        bid_price, ask_price, amount = util.find_profit(data[7], data[4])
	if amount != 0: # huobi sell binance buy
		bid_price_sym2 = bid_price; ask_price_sym2 = ask_price
		amount_sym2 = amount; flag_sym2 = -1

	hedge_data.append([log_date, flag_sym1, bid_price_sym1, ask_price_sym1, amount_sym1, flag_sym2, bid_price_sym2, ask_price_sym2, amount_sym2])

hedge_data_clean = []
hedge_data_clean.append(hedge_data[0]); amo = hedge_data[0][-1]
for i in range(1, len(hedge_data)):
        if hedge_data[i][-1] == amo: continue
        else:
                amo = hedge_data[i][-1];
                hedge_data_clean.append(hedge_data[i])

count = 0
for i in hedge_data_clean:
	if i[1] or i[5]:
		print(i)
		count += 1
print(count)

# close connection
conn.close()
