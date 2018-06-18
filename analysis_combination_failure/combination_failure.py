import MySQLdb
import json
import numpy as np

# init setup
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_analysis'

# fetch data
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
# sql = "select ask_amount, case when (filled_amount-ask_amount)/ask_amount>=-0.0005 then 1 else 0 end as flag, query_price, depth from (select query_amount/query_price as ask_amount, filled_amount, depth, query_price from btc_trade.combination_trade_info where trade_side='BUY' and market='HUOBI' and substring(create_time, 1, 10)>='2018-03-20' and symbol='trxeth' and filled_amount>3000) a"
sql = "select a.flag, a.query_price as huobi_price, b.query_price as binance_price, (b.query_price-a.query_price)/b.query_price as diff_rate, a.filled_amount from (select filled_amount, case when (filled_amount-query_amount/query_price)/filled_amount>=-0.0005 then 1 else 0 end as flag, query_price, trade_pair_id from btc_trade.combination_trade_info where market='HUOBI' and trade_side='BUY' and substring(create_time, 1, 10)>='2018-03-20' and symbol='trxeth') a join (select query_price, trade_pair_id from btc_trade.combination_trade_info where market='BINANCE' and trade_side='SELL' and substring(create_time, 1, 10)>='2018-03-21' and symbol='trxeth' and filled_amount>0 and filled_amount<6000) b on a.trade_pair_id=b.trade_pair_id"
cur.execute(sql)
res = []
for row in cur.fetchall():
	# res.append([row[0], row[1], row[2], json.loads(row[3])])
	res.append([row[0], row[1], row[2], row[3], row[4]])

# analyze data
price_gap = {0 : [], 1 : []}
for i in range(0, len(res)):
	price_gap[res[i][0]].append(res[i][3])
print(len(price_gap[1])*1.0/(len(price_gap[0])+len(price_gap[1])))
print((len(price_gap[0])+len(price_gap[1])))
'''
for i in range(0, len(res)):
	price_gap_rate = (float(res[i][3][1][0]) - float(res[i][3][0][0])) / float(res[i][3][0][0])
	price_gap[res[i][1]].append(price_gap_rate)
'''

# close connection
conn.close()
