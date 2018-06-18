# -*- coding=utf-8 -*-
"""
获取火币的交易订单信息，使用WebSocket形式
"""
from commandr import command, Run
import json
from redis import Redis
from datetime import datetime
import time
from websocket import create_connection
import zlib
import traceback
from coin.lib.config import TIMEOUT, RECONNECT_TIME
from coin.lib.utils import get_redis_key, bigcoin_set, Market, ip
from coin.model.exception_info import ExceptionInfoModel
from coin.model.base import clear_dbsession


def start_websocket(coin_pair_list, depth):
    """
    建立连接，监听频道
    :param coin_pair_list:
    :param depth:
    :return:
    """
    ws = create_connection('wss://api.huobi.pro/ws', timeout=TIMEOUT)
    for coin1, coin2 in coin_pair_list:
        client_id = 'fetch_btc_info_{}_{}'.format(coin1, coin2)
        # 火币是大币在后（除了面对ustd）
        if coin1.lower() in bigcoin_set:
            coin_symbol = '{}{}'.format(coin2, coin1).lower()
        else:
            coin_symbol = '{}{}'.format(coin1, coin2).lower()
        signle = {
            "sub": "market.{}.depth.{}".format(coin_symbol, depth),
            "id": client_id
        }
        ws.send(json.dumps(signle))
        res = ws.recv()
        print("{}|Sub|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                 zlib.decompress(res, 16+zlib.MAX_WBITS)))
    return ws


@command('fetch')
def run(coin_pair, depth='step0'):
    """

    :param coin_pair: string coin1:coin2|coin1:coin2
    :param depth: step0 - step5
    :return:
    """
    rds = Redis(host='localhost', port=6379, db=0)
    pair_part = coin_pair.split('|')
    coin_pair_list = [item.split(':') for item in pair_part]
    ws = start_websocket(coin_pair_list, depth)
    start_run = time.time()
    while 1:
        try:
            unziped_message = json.loads(zlib.decompress(ws.recv(), 16+zlib.MAX_WBITS))
            if 'ping' in unziped_message:
                print("{}|PING|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                          unziped_message))
                ws.send(json.dumps({'pong': unziped_message['ping']}))
            elif 'subbed' in unziped_message:
                print("{}|Sub|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                         unziped_message['subbed']))
            else:  # 收到的是数据
                if 'ch' in unziped_message:
                    coin_symbol = unziped_message['ch'].split('.')[1]
                    if coin_symbol[-3:] in bigcoin_set:
                        coin1 = coin_symbol[-3:]
                        coin2 = coin_symbol[:-3]
                    else:
                        raise Exception('UnExcepted Coin Info {}'.format(coin_symbol))
                    start = time.time()
                    redis_key = get_redis_key(market=Market.HUOBI, coin1=coin1, coin2=coin2)
                    price_data = unziped_message['tick']
                    # 序列化复杂数据
                    price_data['ts'] = unziped_message['ts']
                    price_data['bids'] = json.dumps(price_data['bids'][:10])
                    price_data['asks'] = json.dumps(price_data['asks'][:10])
                    rds.hmset(redis_key, price_data)
                    end = time.time()
                    print("{}|Received|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), price_data))
                    print("{}|SetRedis|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                     redis_key, end-start))
                else:
                    print("{}|UnExceptedMessage|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                           unziped_message))
            # 建立连接一段时间之后准备重建连接
            current_time = time.time()
            if current_time - start_run > RECONNECT_TIME:  # 设置为10小时 10*60*60=36000
                print("{}|ReConnect".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                ws.close()
                ws = start_websocket(coin_pair_list, depth)
                start_run = current_time

        except Exception as e:
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            try:  # 出现异常之后重新建立连接
                ws.close()
            except:
                pass
            try:
                ExceptionInfoModel(host=ip, source='FETCH_HUOBI_DEPTH', message=e.message,
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
    # test_depth = 'step0'
    # run(test_coin_pair_list, test_depth)
    Run()
