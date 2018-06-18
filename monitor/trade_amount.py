import MySQLdb
import sys

def get_trade_amount(market, trade_side, query_amount, query_price, filled_amount):
	if market == 'BINANCE':
		return query_amount * query_price
	elif market == 'HUOBI' and trade_side == 'BUY':
		return query_amount
	elif market == 'HUOBI' and trade_side == 'SELL':
		return filled_amount
	elif market == 'OKEX' and trade_side == 'BUY':
		return query_amount
	elif market == 'OKEX' and trade_side == 'SELL':
		return filled_amount
	else:
		return 0

# init setup
d = sys.argv[1]
h = sys.argv[2]
hour = d + ' ' + h
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_trade'

# fetch data
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select combination, market, trade_side, query_amount, query_price, filled_amount from combination_trade_info where substring(create_time, 1, 13)='{}'".format(hour)
print(sql)
cur.execute(sql)
row = []
for i in cur.fetchall():
        row.append(i)

# calculate trade amount
res = {}
for data in row:
	combination = data[0]
	market = data[1]
	trade_side = data[2]
	query_amount = data[3]
	query_price = data[4]
	filled_amount = data[5]
	trade_amount = get_trade_amount(market, trade_side, query_amount, query_price, filled_amount)
	if combination not in res:
		res[combination] = trade_amount
	else:
		res[combination] += trade_amount

# insert into mysql table
for combination in res.keys():
	trade_amount = res[combination]
	sql = "insert into combination_trade_amount (combination, trade_amount, hour) VALUES ('{}', {}, '{}')".format(combination, trade_amount, hour)
	cur.execute(sql)
	conn.commit()

# disconnect
conn.close()
