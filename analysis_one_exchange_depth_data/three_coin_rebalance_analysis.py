import MySQLdb
import json
import util

# init setup
host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
user = 'taohuashan'
passwd = '123@admin'
db = 'btc_analysis'

# fetch data
exchange = 'binance'
symbol1 = 'iost/btc'
symbol2 = 'iost/eth'
symbol3 = 'eth/btc'
conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cur = conn.cursor()
sql = "select * from one_exchange_three_coin_depth where exchange='{}' and symbol='{}|{}|{}' order by log_time desc".format(exchange, symbol1, symbol2, symbol3)
cur.execute(sql)
res = []
for row in cur.fetchall():
	res.append([row[0], json.loads(row[3]), json.loads(row[4]), json.loads(row[5]), json.loads(row[6]), json.loads(row[7]), json.loads(row[8])])

# analyze data
hedge_data = []
for i in range(0, len(res)):
	data = res[i][:]
        if not data[1] or not data[2] or not data[3] or not data[4] or not data[5] or not data[6]:
                continue
	log_date = data[0]
	sym1_bids = data[1][0]
	sym1_asks = data[2][0]
	sym2_bids = data[3][0]
	sym2_asks = data[4][0]
	sym3_bids = data[5][0]
	sym3_asks = data[6][0]
	flag = 0
	sym1_amount = 0
	sym2_amount = 0
	sym3_amount = 0
	if (1/sym1_asks[0]*sym2_bids[0]*sym3_bids[0]-1) > 0.002:
		flag = 1
		hedge_data.append([log_date, flag, data[2], data[3], data[5]])
	if (1/sym3_asks[0]/sym2_asks[0]*sym1_bids[0]-1) > 0.002:
		flag = -1
		hedge_data.append([log_date, flag, data[1], data[4], data[6]])

'''
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
'''

# close connection
conn.close()
