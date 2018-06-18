# author: ouyan
# date: 2018-03-10
# comment: fetch data api connection

import requests
import MySQLdb

class MySQLClient():
        def __init__(self):
                self.host = 'rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com'
                self.user = 'taohuashan'
                self.passwd = '123@admin'
                self.db = 'btc_analysis'
                self.conn = None
                self.cur = None

        def connect(self):
                self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
                self.cur = self.conn.cursor()

        def disconnect(self):
                self.conn.close()

        def exe_sql(self, sql):
                try:
                        self.cur.execute(sql)
                        self.conn.commit()
                        return True
                except Exception as e:
                        print(e)
                        print(sql)
                        return False

        def insert_depth_data(self, log_time, symbol, exchange, symbol1_bids, symbol1_asks, symbol2_bids, symbol2_asks, symbol3_bids, symbol3_asks):
                sql = '''
                INSERT INTO one_exchange_three_coin_depth (log_time, symbol, exchange, symbol1_bids, symbol1_asks, symbol2_bids, symbol2_asks, symbol3_bids, symbol3_asks) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                '''
                res = self.exe_sql(sql % (log_time, symbol, exchange, symbol1_bids, symbol1_asks, symbol2_bids, symbol2_asks, symbol3_bids, symbol3_asks))
                return res

class HuobiClient():
        def __init__(self):
                self.base_url = 'https://api.huobi.pro/'

        def get_depth_data(self, symbol):
                url = self.base_url + 'market/depth?symbol=' + symbol + '&type=step0'
                try:
                        res = requests.get(url)
                        data = res.json()
                        bids = []; asks = []
                        for item in data['tick']['bids'][:5]:
                                bids.append([float(item[0]), float(item[1])])
                        for item in data['tick']['asks'][:5]:
                                asks.append([float(item[0]), float(item[1])])
                        return bids, asks
                # except requests.RequestException as e:
                except:
                        print("huobi api error")
                        return None, None

class BinanceClient():
        def __init__(self):
                self.base_url = 'https://api.binance.com/'

        def get_depth_data(self, symbol):
                url = self.base_url + 'api/v1/depth?symbol=' + symbol + '&limit=10'
                try:
                        res = requests.get(url)
                        data = res.json()
                        bids = []; asks = []
                        for item in data['bids'][:5]:
                                bids.append([float(item[0]), float(item[1])])
                        for item in data['asks'][:5]:
                                asks.append([float(item[0]), float(item[1])])
                        return bids, asks
                # except requests.RequestException as e:
                except:
                        print("binance api error")
                        return None, None
