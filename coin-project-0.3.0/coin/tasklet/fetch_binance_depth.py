# -*- coding=utf-8 -*-
"""
获取币安的订单信息
"""
from commandr import command, Run
import certifi
import json
from redis import Redis
from datetime import datetime
import os
import time
from websocket import create_connection
import traceback
from coin.lib.utils import get_redis_key, Market, bigcoin_set, ip
from coin.lib.config import TIMEOUT, RECONNECT_TIME
from coin.model.base import clear_dbsession
from coin.model.exception_info import ExceptionInfoModel


def start_websocket(coin_pair_list, depth):
    """
    启动socket，监听频道
    :param coin_pair_list:
    :param depth:
    :return:
    """
    symble_str = '/'.join(['{}{}@depth{}'.format(coin1, coin2, depth).lower() for coin1, coin2 in coin_pair_list])
    full_url = 'wss://stream.binance.com:9443/stream?streams={}'.format(symble_str)
    print("{}|ConnectUrl|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), full_url))
    ws = create_connection(full_url, timeout=TIMEOUT)
    return ws


@command('fetch')
def run(coin_pair, depth=10):
    """
    A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark
    :param coin_pair: coin1:coin2|coin1:coin2 小币在前，大币在后
    :param depth: 5 / 10 / 20
    :return:
    """
    os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = certifi.where()
    rds = Redis(host='localhost', port=6379, db=0)
    pair_part = coin_pair.split('|')
    coin_pair_list = [item.split(':') for item in pair_part]
    ws = start_websocket(coin_pair_list, depth)
    start_run = time.time()
    while 1:
        try:
            res = json.loads(ws.recv())
            print("{}|Received|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                          res))
            if 'stream' in res:
                coin_info = res['stream'].split('@')[0]
                if coin_info[-3:] in bigcoin_set:
                    coin1 = coin_info[-3:]
                    coin2 = coin_info[:-3]
                else:
                    raise Exception('UnExcepted Coin Info {}'.format(coin_info))
                start = time.time()
                redis_key = get_redis_key(market=Market.BINANCE, coin1=coin1, coin2=coin2)
                price_data = res['data']
                # 序列化复杂数据
                price_data['ts'] = int(time.time() * 1000)
                # 保持字符串，不要随便转换为float损失精度
                price_data['bids'] = json.dumps([[item[0], item[1]] for item in price_data['bids']])
                price_data['asks'] = json.dumps([[item[0], item[1]] for item in price_data['asks']])
                rds.hmset(redis_key, price_data)
                end = time.time()
                print("{}|SetRedis|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                 redis_key, end-start))
            else:
                print("{}|UnExceptedMessage|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                       res))
            run_time = time.time() - start_run
            if run_time > RECONNECT_TIME:  # 不超过24小时，保险点，设置为10小时 10*60*60=36000
                print("{}|ReConnect".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                ws.close()
                ws = start_websocket(coin_pair_list, depth)
                start_run = time.time()
        except Exception as e:
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            try:
                ws.close()
            except:
                pass
            try:
                ExceptionInfoModel(host=ip, source='FETCH_BINANCE_DEPTH', message=e.message,
                                   log_time=datetime.utcnow()).add()
                clear_dbsession()
            except:
                pass
            for fail_count in xrange(5):
                # 休息10s
                time.sleep(10)
                try:
                    ws = start_websocket(coin_pair_list, depth)
                    start_run = time.time()
                except:
                    print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                   e.message))
                    print("Traceback|{}".format(traceback.format_exc()))
                    # 第五次还不行
                    if fail_count >= 4:
                        raise
                else:
                    break


if __name__ == '__main__':
    # test_coin_pair_list = [('TRX', 'ETH'), ('DGD', 'ETH')]
    # test_coin_pair_list = [('IOST', 'BTC'), ('KNC', 'BTC')]
    # test_depth = 10
    # run(test_coin_pair_list, test_depth)
    Run()
