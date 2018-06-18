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
day = '2018-04-19'

exchange_pair = 'binance/hitbtc'
small_coin = 'xvg'
big_coin = 'btc'

conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select * from two_exchange_hedge_depth where exchange_pair='{}' and symbol='{}/{}' order by log_date desc".format(exchange_pair, small_coin, big_coin)
cur.execute(sql)
res = []
for row in cur.fetchall():
	res.append([row[0], json.loads(row[3]), json.loads(row[4]), json.loads(row[5]), json.loads(row[6])])

pos = []; neg = []
for data in res:
	if data[1] or data[2] or data[3] or data[4]: continue
	# exchange 1 sell, exchange 2 buy
	gap = (data[1][0][0]-data[4][0][0])/(data[1][0][0]+data[4][0][0])*2
	if gap > 0.003: pos.append(gap)
	# exchange 2 sell, exchange 1 buy
	gap = (data[3][0][0]-data[2][0][0])/(data[3][0][0]+data[2][0][0])*2
	if gap < -0.003: neg.append(gap)

print('exchange 1 sell, exchange 2 buy')
print(sum(pos)/len(pos))
print('exchange 2 sell, exchange 1 buy')
print(sum(neg)/len(neg))
