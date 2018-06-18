# author: ouyan
# date: 2018-03-12
# comment: get big market symbols for exchanges

import requests

# parameters
min_btc_binance_market = 500

# get BTC based symbol for binance
binance_url = 'https://api.binance.com/api/v1/ticker/24hr'
res = requests.get(binance_url)
data = res.json()
binance_symbols = []
for row in data:
        symbol = row['symbol']
        if symbol[-3:] == 'BTC':
                price = float(row['weightedAvgPrice'])
                volume = float(row['volume'])
                market = price * volume
                if market > min_btc_binance_market:
                        binance_symbols.append([symbol, market])
print(binance_symbols)

# get BTC based symbol for huobi
huobi_base_url = 'https://api.huobi.pro/market/detail?symbol='
huobi_symbols = []
for symbol in binance_symbols:
        url = huobi_base_url + symbol[0].lower()
        print(url)
        res = requests.get(url)
        data = res.json()
        if data['status'] == 'error': continue
        price_open = float(data['tick']['open'])
        price_close = float(data['tick']['close'])
        price_high = float(data['tick']['high'])
        price_low = float(data['tick']['low'])
        price = (price_open + price_close + price_high + price_low) / 4
        volume = float(data['tick']['amount'])
        market = price * volume
        huobi_symbols.append([symbol[0], market])
print(huobi_symbols)
