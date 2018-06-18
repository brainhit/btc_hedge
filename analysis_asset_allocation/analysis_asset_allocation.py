import requests
import json
from datetime import datetime

# get daily klines data
base_url = 'https://api.binance.com/api/v1/klines?symbol='
kline_btcusdt = requests.get(base_url + 'BTCUSDT' + '&interval=1d').json()
kline_dgdbtc = requests.get(base_url + 'BNBBTC' + '&interval=1d').json()
kline_trxbtc = requests.get(base_url + 'CHATBTC' + '&interval=1d').json()
kline = []

# get aggregate klines data
start_ts = max(kline_btcusdt[0][0], kline_dgdbtc[0][0], kline_trxbtc[0][0])
idx_btcusdt = 0; idx_dgdbtc = 0; idx_trx_btc = 0
for i in range(0, len(kline_btcusdt)):
	if kline_btcusdt[i][0] == start_ts:
		idx_btcusdt = i; break
for i in range(0, len(kline_dgdbtc)):
        if kline_dgdbtc[i][0] == start_ts:
                idx_dgdbtc = i; break
for i in range(0, len(kline_trxbtc)):
        if kline_trxbtc[i][0] == start_ts:
                idx_trxbtc = i; break
agg_price = []
while idx_btcusdt < len(kline_btcusdt) and idx_dgdbtc < len(kline_dgdbtc) and idx_trxbtc < len(kline_trxbtc):
	ts = int(kline_btcusdt[idx_btcusdt][0])
	dt = datetime.utcfromtimestamp(ts/1000)
	log_date = dt.strftime('%Y-%m-%d %H:%M:%S')
	tmp = [log_date, float(kline_btcusdt[idx_btcusdt][4]), float(kline_dgdbtc[idx_dgdbtc][4]), float(kline_trxbtc[idx_trxbtc][4])]
	agg_price.append(tmp)
	idx_btcusdt += 1; idx_dgdbtc += 1; idx_trxbtc += 1

# back test
usdt_rate = 0.5
dgd_rate = 0.25
trx_rate = 0.25
begin_idx = 0
log_date = [agg_price[begin_idx][0]]
btc_amount = [1]
usdt_amount = usdt_rate*agg_price[begin_idx][1]
dgd_amount = dgd_rate/agg_price[begin_idx][2]
trx_amount = trx_rate/agg_price[begin_idx][3]
for i in range(begin_idx+1, len(agg_price)):
	log_date.append(agg_price[i][0])
	price_btcusdt = agg_price[i][1]
	price_dgdbtc = agg_price[i][2]
	price_trxbtc = agg_price[i][3]
	cur_btc_amount = usdt_amount/price_btcusdt + dgd_amount*price_dgdbtc + trx_amount*price_trxbtc
	btc_amount.append(cur_btc_amount)
print(log_date)
print(btc_amount)
