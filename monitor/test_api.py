import requests
import time
from binance.client import Client

num = 10

# binance request time
API_KEY = 'cJFBXQBnmfT4NHxS6sUBOqNe7ujOM8XifOPMEgMR7qHqsf03dLZVs2waDToZsyvo'
SECRET = '2T1V1LXVPae6uzI65EL4DDuG7ypqu1wcOfk1bnSOM5IMdcIEp2xBmEsiDxZt5ITz'
client = Client(API_KEY, SECRET)
aa = 0; bb = 0; cc = 0
for i in range(0, num):
        s = time.time()
        t = client.get_server_time()['serverTime']
        e = time.time()
        aa += t-1000*s
        bb += 1000*e-t
        cc += 1000*e-1000*s
aa /= num; bb /= num; cc /= num
print('binance api')
print('send time: ' + str(aa))
print('get time: ' + str(bb))
print('total time: ' + str(cc))

# huobi request time
url = 'https://api.huobipro.com/v1/common/timestamp'
aa = 0; bb = 0; cc = 0
for i in range(0, num):
        s = time.time()
        res = requests.get(url)
        e = time.time()
        t = res.json()['data']
        aa += t-1000*s
        bb += 1000*e-t
        cc += 1000*e-1000*s
aa /= num; bb /= num; cc /= num
print('huobi api')
print('send time: ' + str(aa))
print('get time: ' + str(bb))
print('total time: ' + str(cc))
