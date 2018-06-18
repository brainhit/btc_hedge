# -*- coding=utf-8 -*-
from commandr import command, Run
import json
from datetime import datetime
from redis import Redis
import time
from websocket import create_connection
import traceback
from coin.lib.coin_exception import SubChannelError
from coin.lib.config import TIMEOUT, RECONNECT_TIME
from coin.lib.utils import get_redis_key, bigcoin_set, Market, ip
from coin.model.base import clear_dbsession
from coin.model.exception_info import ExceptionInfoModel


def start_websocket(coin_pair_list):
    """
    建立连接，监听频道
    :param coin_pair_list:
    :return:
    """
    ws = create_connection('wss://api.zb.com:9999/websocket', timeout=TIMEOUT)
    # single_list = list()
    for coin1, coin2 in coin_pair_list:
        # ZB是大币在后
        if coin1.lower() in bigcoin_set:
            coin_symbol = '{}{}'.format(coin2, coin1).lower()
        else:
            coin_symbol = '{}{}'.format(coin1, coin2).lower()
        # print '{}_depth'.format(coin_symbol)
        signle = {
            'event': 'addChannel',
            'channel': '{}_depth'.format(coin_symbol)
        }
        ws.send(json.dumps(signle))
        # single_list.append(signle)
    # ws.send(json.dumps(single_list))
    return ws


@command('fetch')
def run(coin_pair):
    """

    :param coin_pair: coin_pair: coin1:coin2|coin1:coin2 小币在前，大币在后
    :return:
    """
    rds = Redis(host='localhost', port=6379, db=0)
    pair_part = coin_pair.split('|')
    coin_pair_list = [item.split(':') for item in pair_part]
    ws = start_websocket(coin_pair_list)
    start_run = time.time()
    while 1:
        try:
            message = json.loads(ws.recv())
            if 'dataType' in message and message['dataType'] == 'depth':
                coin_info = message['channel'].split('_')[0]
                if coin_info[-3:] in bigcoin_set:
                    coin1 = coin_info[-3:]
                    coin2 = coin_info[:-3]
                else:
                    raise Exception('UnExcepted Coin Info {}'.format(coin_info))
                redis_key = get_redis_key(market=Market.ZB, coin1=coin1, coin2=coin2)
                price_data = dict()
                # 序列化复杂数据
                # 返回的时间戳为秒级别，不可用
                price_data['ts'] = int(time.time() * 1000)
                price_data['version'] = price_data['ts']
                # 保持字符串，不要随便转换为float损失精度
                price_data['bids'] = json.dumps([[str(item[0]), str(item[1])] for item in message['bids']])
                price_data['asks'] = json.dumps([[str(item[0]), str(item[1])] for item in message['asks']])
                start = time.time()
                rds.hmset(redis_key, price_data)
                end = time.time()
                print("{}|SetRedis|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                 redis_key, end-start))
            # 建立连接一段时间之后准备重建连接
            current_time = time.time()
            if current_time - start_run > RECONNECT_TIME:  # 设置为10小时 10*60*60=36000
                print("{}|ReConnect".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                ws.close()
                ws = start_websocket(coin_pair_list)
                start_run = current_time
            # elif current_time - ping_time > 10:  # 每10秒ping一次
            #     ws.send(json.dumps({'event': 'ping'}))
            #     ping_time = current_time
        except Exception as e:
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            try:  # 出现异常之后重新建立连接
                ws.close()
            except:
                pass
            try:
                ExceptionInfoModel(host=ip, source='FETCH_ZB_DEPTH', message=e.message,
                                   log_time=datetime.utcnow()).add()
                clear_dbsession()
            except:
                pass
            for fail_count in xrange(5):
                # 休息10s
                time.sleep(10)
                try:
                    ws = start_websocket(coin_pair_list)
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
    # test_coin_pair_list = [('IOST', 'BTC'), ('TRX', 'ETH'), ('DGD', 'ETH')]
    # test_coin_pair_list = [('IOST', 'BTC'), ('TRX', 'ETH')]
    # test_depth = 10
    # run(test_coin_pair_list, test_depth)
    Run()
