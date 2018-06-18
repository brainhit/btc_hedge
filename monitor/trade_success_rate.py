import MySQLdb
import sys

def get_trade_success_flag(market, trade_side, query_amount, query_price, filled_amount):
	if (market == 'HUOBI' or market == 'OKEX') and trade_side == 'BUY':
		trade_success_flag = ((filled_amount - query_amount/query_price) / filled_amount >= -0.0005)
		return 1, trade_success_flag
	if (market == 'HUOBI' or market == 'OKEX') and trade_side == 'SELL':
		trade_success_flag = ((filled_amount/query_price - query_amount) / query_amount >= -0.0005)
		return 1, trade_success_flag
	return 0, 0

# init setup
day = sys.argv[1]
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_trade'

# fetch data
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select combination, market, trade_side, query_amount, query_price, filled_amount from combination_trade_info where substring(create_time, 1, 10)='{}'".format(day)
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
	if not combination or not market or not trade_side or not query_amount or not query_price or not filled_amount: continue
	flag_trade, flag_success = get_trade_success_flag(market, trade_side, query_amount, query_price, filled_amount)
	if combination not in res:
		res[combination] = [flag_trade, flag_success]
	else:
		res[combination][0] += flag_trade
		res[combination][1] += flag_success

# insert into mysql table
for combination in res.keys():
	trade_num = res[combination][0]
	trade_success_rate = 1.0 * res[combination][1] / res[combination][0]
	sql = "insert into combination_trade_success_rate (combination, trade_success_rate, trade_num, dt) VALUES ('{}', {}, {}, '{}')".format(combination, trade_success_rate, trade_num, day)
	cur.execute(sql)
	conn.commit()

# disconnect
conn.close()
