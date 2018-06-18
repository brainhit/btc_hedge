# -*- coding=utf-8 -*-
from websocket import create_connection
import json
import zlib

ws = create_connection('wss://api.huobi.pro/ws', timeout=5)
client_id = "fetch_btc_info_iost_btc"
signle = {"sub" : "market.iostbtc.depth.step0", "id" : client_id}
ws.send(json.dumps(signle))
res = ws.recv()
client_id = "fetch_btc_info_trx_eth"
signle = {"sub" : "market.trxeth.depth.step0", "id" : client_id}
ws.send(json.dumps(signle))
res = ws.recv()

unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
print(unziped_message)
unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
print(unziped_message)
unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
print(unziped_message)
unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
print(unziped_message)
ws.close()
