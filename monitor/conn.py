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

        def insert_api_speed_data(self, exchange, forward_time, backward_time, total_time, log_time):
                sql = '''
                INSERT INTO api_speed (exchange, forward_time, backward_time, total_time, log_time) VALUES ('%s', %s, %s, %s, '%s')
                '''
                res = self.exe_sql(sql % (exchange, forward_time, backward_time, total_time, log_time))
                return res
