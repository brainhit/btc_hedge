# author: ouyan
# date: 2018-03-19
# comment: get the api speed

import requests
import time
from binance.client import Client
import conn
from datetime import datetime

mysql_client = conn.MySQLClient()
mysql_client.connect()
API_KEY = 'cJFBXQBnmfT4NHxS6sUBOqNe7ujOM8XifOPMEgMR7qHqsf03dLZVs2waDToZsyvo'
SECRET = '2T1V1LXVPae6uzI65EL4DDuG7ypqu1wcOfk1bnSOM5IMdcIEp2xBmEsiDxZt5ITz'
client = Client(API_KEY, SECRET)

num = 10

while 1:
	try:
		# binance request time
		forward_time = 0; back_time = 0; total_time = 0
		for i in range(0, num):
			s = time.time()
			t = client.get_server_time()['serverTime']
			e = time.time()
			forward_time += t-1000*s
			back_time += 1000*e-t
			total_time += 1000*e-1000*s
		ts = int(round(time.time()))
		dt = datetime.utcfromtimestamp(ts)
		log_time = dt.strftime('%Y-%m-%d %H:%M:%S')
		forward_time /= num; back_time /= num; total_time /= num
		mysql_client.insert_api_speed_data('binance', forward_time, back_time, total_time, log_time)
	except:
		print('binance api error')

	try:
		# huobi request time
		url = 'https://api.huobipro.com/v1/common/timestamp'
		forward_time = 0; back_time = 0; total_time = 0
		for i in range(0, num):
			s = time.time()
			res = requests.get(url)
			e = time.time()
			t = res.json()['data']
			forward_time += t-1000*s
			back_time += 1000*e-t
			total_time += 1000*e-1000*s 
		dt = datetime.utcfromtimestamp(ts)
		log_time = dt.strftime('%Y-%m-%d %H:%M:%S')
		forward_time /= num; back_time /= num; total_time /= num
		mysql_client.insert_api_speed_data('huobi', forward_time, back_time, total_time, log_time)
	except:
		print('huobi api error')
	time.sleep(5)

# disconnect
mysql_client.disconnect()
