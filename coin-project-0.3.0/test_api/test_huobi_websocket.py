# -*- coding=utf-8 -*-
from websocket import create_connection, enableTrace, WebSocketApp
from uuid import uuid4
import json
import zlib
import time


def test_ping():
    ws = create_connection('wss://api.huobi.pro/ws')
    ws.send(json.dumps({'ping': int(time.time())}))
    res = ws.recv()
    print("Received '%s'" % res)
    print("Received '%s'" % zlib.decompress(res, 16+zlib.MAX_WBITS))


def test_btcusdt_depth():
    client_id = str(uuid4())
    print 'client_id', client_id

    # def on_message(ws, message):
    #     unziped_message = json.loads(zlib.decompress(message, 16+zlib.MAX_WBITS))
    #     print("Received '%s'" % unziped_message)
    #     if 'ping' in unziped_message:
    #         ws.send(json.dumps({'pong': unziped_message['ping']}))
    #
    # def on_error(ws, error):
    #     print(error)
    #
    # def on_close(ws):
    #     print("### closed ###")
    #
    # def on_open(ws):
    #     print ("ON OPEN")
    #     signle = {
    #         "sub": "market.btcusdt.depth.step0",
    #         "id": client_id
    #     }
    #     ws.send(json.dumps(single))
    #     print ('ON OPEN AFTER SEND')
    #     res = ws.recv()
    #     print("ON OPEN Received '%s'" % zlib.decompress(res, 16+zlib.MAX_WBITS))
    # enableTrace(True)
    ws = create_connection('wss://api.huobi.pro/ws')
    signle = {
        "sub": "market.btcusdt.depth.step5",
        "id": client_id
    }
    ws.send(json.dumps(signle))
    res = ws.recv()
    print("Received '%s'" % zlib.decompress(res, 16+zlib.MAX_WBITS))
    while 1:
        unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
        print("Received '%s'" % unziped_message)
        if 'ping' in unziped_message:
            ws.send(json.dumps({'pong': unziped_message['ping']}))


if __name__ == '__main__':
    test_btcusdt_depth()
