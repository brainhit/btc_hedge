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


def start_websocket(coin_pair_list, depth):
    """
    建立连接，监听频道
    :param coin_pair_list:
    :param depth: 5/10/20
    :return:
    """
    ws = create_connection('wss://real.okex.com:10441/websocket', timeout=TIMEOUT)
    single_list = list()
    for coin1, coin2 in coin_pair_list:
        # 火币是大币在后（除了面对ustd）
        if coin1.lower() in bigcoin_set:
            coin_symbol = '{}_{}'.format(coin2, coin1).lower()
        else:
            coin_symbol = '{}_{}'.format(coin1, coin2).lower()
        signle = {
            'event': 'addChannel',
            'channel': 'ok_sub_spot_{}_depth_{}'.format(coin_symbol, depth)
        }
        single_list.append(signle)
    ws.send(json.dumps(single_list))
    ws.send(json.dumps({'event': 'ping'}))
    return ws


@command('fetch')
def run(coin_pair, depth=10):
    """

    :param coin_pair: coin_pair: coin1:coin2|coin1:coin2 小币在前，大币在后
    :param depth: step0 - step5
    :return:
    """
    rds = Redis(host='localhost', port=6379, db=0)
    pair_part = coin_pair.split('|')
    coin_pair_list = [item.split(':') for item in pair_part]
    ws = start_websocket(coin_pair_list, depth)
    start_run = ping_time = time.time()
    while 1:
        try:
            message = json.loads(ws.recv())
            if isinstance(message, list):  # 订阅成功信息或者深度信息
                for item in message:
                    if item['channel'] == 'addChannel':
                        if item['data']['result'] is True:
                            print("{}|SubChannel|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                            item['data']['channel']))
                        else:
                            raise SubChannelError("{}|SubChannelFail|{}".format(
                                datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), item['data']['channel']))
                    else:  # 数据
                        channel = item['channel']
                        channel_parts = channel.split('_')
                        coin1 = channel_parts[-4]
                        coin2 = channel_parts[-3]
                        redis_key = get_redis_key(market=Market.OKEX, coin1=coin1, coin2=coin2)
                        price_data = item['data']
                        price_data['ts'] = price_data['timestamp']
                        price_data['version'] = price_data['timestamp']
                        price_data.pop('timestamp')
                        price_data['bids'] = json.dumps(price_data['bids'])
                        price_data['asks'] = json.dumps(price_data['asks'])
                        start = time.time()
                        rds.hmset(redis_key, price_data)
                        end = time.time()
                        print("{}|Received|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), price_data))
                        print("{}|SetRedis|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                         redis_key, end-start))
            else:
                if 'event' in message and message['event'] == 'pong':
                    print("{}|ReceivedPong|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                                      message))
            # if 'ping' in unziped_message:
            #     print("{}|PING|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            #                               unziped_message))
            #     ws.send(json.dumps({'pong': unziped_message['ping']}))
            # elif 'subbed' in unziped_message:
            #     print("{}|Sub|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            #                              unziped_message['subbed']))
            # else:  # 收到的是数据
            #     if 'ch' in unziped_message:
            #         coin_symbol = unziped_message['ch'].split('.')[1]
            #         if coin_symbol[-3:] in bigcoin_set:
            #             coin1 = coin_symbol[-3:]
            #             coin2 = coin_symbol[:-3]
            #         else:
            #             raise Exception('UnExcepted Coin Info {}'.format(coin_symbol))
            #         start = time.time()
            #         redis_key = get_redis_key(market=Market.HUOBI, coin1=coin1, coin2=coin2)
            #         price_data = unziped_message['tick']
            #         # 序列化复杂数据
            #         price_data['ts'] = unziped_message['ts']
            #         price_data['bids'] = json.dumps(price_data['bids'][:10])
            #         price_data['asks'] = json.dumps(price_data['asks'][:10])
            #         rds.hmset(redis_key, price_data)
            #         end = time.time()
            #         print("{}|Received|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), price_data))
            #         print("{}|SetRedis|{}|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            #                                          redis_key, end-start))
            #     else:
            #         print("{}|UnExceptedMessage|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            #                                                unziped_message))
            # 建立连接一段时间之后准备重建连接
            current_time = time.time()
            if current_time - start_run > RECONNECT_TIME:  # 设置为10小时 10*60*60=36000
                print("{}|ReConnect".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))
                ws.close()
                ws = start_websocket(coin_pair_list, depth)
                start_run = current_time
            elif current_time - ping_time > 10:  # 每10秒ping一次
                ws.send(json.dumps({'event': 'ping'}))
                ping_time = current_time
        except Exception as e:
            print("{}|Exception|{}".format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                           e.message))
            print("Traceback|{}".format(traceback.format_exc()))
            try:  # 出现异常之后重新建立连接
                ws.close()
            except:
                pass
            try:
                ExceptionInfoModel(host=ip, source='FETCH_OKEX_DEPTH', message=e.message,
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
    # test_coin_pair_list = [('IOST', 'BTC'), ('TRX', 'ETH'), ('DGD', 'ETH')]
    # test_coin_pair_list = [('IOST', 'BTC'), ('TRX', 'ETH')]
    # test_depth = 10
    # run(test_coin_pair_list, test_depth)
    Run()
