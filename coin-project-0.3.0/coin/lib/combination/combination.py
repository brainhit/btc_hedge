# -*- coding=utf-8 -*-
"""
用户账户组合
"""
from datetime import datetime
from coin.lib.utils import aes_encrypt, aes_decrypt, Status
from coin.lib.coin_exception import CombinationNotExistError
from coin.model.base import get_dbsession
from coin.model.combination import CombinationModel


class Combination(object):

    def __init__(self, id, combination, user, first_market, second_market, big_coin, small_coin,
                 big_coin_amount, small_coin_amount, trade_threshold, first_market_api_key, first_market_api_secret,
                 second_market_api_key, second_market_api_secret, status='Active',
                 huobi_account=None, huobipoint_account=None):
        self.id = id
        self.combination = combination
        self.user = user
        self.first_market = first_market
        self.second_market = second_market
        self.big_coin = big_coin
        self.small_coin = small_coin
        self.big_coin_amount = big_coin_amount
        self.small_coin_amount = small_coin_amount
        self.trade_threshold = trade_threshold
        self.first_market_api_key = first_market_api_key
        self.first_market_api_secret = first_market_api_secret
        self.second_market_api_key = second_market_api_key
        self.second_market_api_secret = second_market_api_secret
        self.status = status
        self.huobi_account = huobi_account
        self.huobipoint_account = huobipoint_account

    def __repr__(self):
        return u'id: {id}, combination: {combination}, user: {user}, first_market: {first_market}, ' \
               u'second_market: {second_market}, big_coin: {big_coin}, small_coin: {small_coin},' \
               u'big_coin_amount: {big_coin_amount}, small_coin_amount: {small_coin_amount},' \
               u'huobi_account: {huobi_account}, trade_threshold: {trade_threshold}, ' \
               u'first_market_api_key: {first_market_api_key}, first_market_api_secret: {first_market_api_secret}, ' \
               u'second_market_api_key: {second_market_api_key}, ' \
               u'second_market_api_secret: {second_market_api_secret}, ' \
               u'status: {status}, huobipoint_account: {huobipoint_account}'.\
            format(id=self.id, combination=self.combination, user=self.user, first_market=self.first_market,
                   second_market=self.second_market, big_coin=self.big_coin, small_coin=self.small_coin,
                   big_coin_amount=self.big_coin_amount, small_coin_amount=self.small_coin_amount,
                   trade_threshold=self.trade_threshold, first_market_api_key=self.first_market_api_key,
                   first_market_api_secret=self.first_market_api_secret,
                   second_market_api_key=self.second_market_api_key,
                   second_market_api_secret=self.second_market_api_secret, status=self.status,
                   huobi_account=self.huobi_account, huobipoint_account=self.huobipoint_account)

    @classmethod
    def all(cls):
        """
        获取所有组合
        :return: combination object list
        """
        session = get_dbsession()
        try:
            db_list = session.query(CombinationModel).all()
            res_list = list()
            for _db in db_list:
                res_list.append(cls(id=_db.id, combination=_db.combination, user=_db.user,
                                    first_market=_db.first_market, second_market=_db.second_market,
                                    big_coin=_db.big_coin, small_coin=_db.small_coin,
                                    big_coin_amount=_db.big_coin_amount, small_coin_amount=_db.small_coin_amount,
                                    trade_threshold=_db.trade_threshold,
                                    first_market_api_key=aes_decrypt(_db.first_market_api_key),
                                    first_market_api_secret=aes_decrypt(_db.first_market_api_secret),
                                    second_market_api_key=aes_decrypt(_db.second_market_api_key),
                                    second_market_api_secret=aes_decrypt(_db.second_market_api_secret),
                                    status=_db.status,
                                    huobi_account=_db.huobi_account, huobipoint_account=_db.huobipoint_account))
            session.commit()
        except:
            session.rollback()
            raise
        return res_list

    @classmethod
    def all_active(cls):
        """
        获取所有组合
        :return: combination object list
        """
        session = get_dbsession()
        try:
            db_list = session.query(CombinationModel).filter_by(status=Status.Active).all()
            res_list = list()
            for _db in db_list:
                res_list.append(cls(id=_db.id, combination=_db.combination, user=_db.user,
                                    first_market=_db.first_market, second_market=_db.second_market,
                                    big_coin=_db.big_coin, small_coin=_db.small_coin,
                                    big_coin_amount=_db.big_coin_amount, small_coin_amount=_db.small_coin_amount,
                                    trade_threshold=_db.trade_threshold,
                                    first_market_api_key=aes_decrypt(_db.first_market_api_key),
                                    first_market_api_secret=aes_decrypt(_db.first_market_api_secret),
                                    second_market_api_key=aes_decrypt(_db.second_market_api_key),
                                    second_market_api_secret=aes_decrypt(_db.second_market_api_secret),
                                    status=_db.status,
                                    huobi_account=_db.huobi_account, huobipoint_account=_db.huobipoint_account))
            session.commit()
        except:
            session.rollback()
            raise
        return res_list

    @classmethod
    def fetch_by_combination(cls, combination):
        """
        获取指定组合
        :param combination:
        :return:
        """
        session = get_dbsession()
        try:
            _db = session.query(CombinationModel).filter_by(combination=combination).one_or_none()
            if _db is None:
                raise CombinationNotExistError(u'Combination of {} not exist'.format(combination))
            res = cls(id=_db.id, combination=_db.combination, user=_db.user,
                      first_market=_db.first_market, second_market=_db.second_market,
                      big_coin=_db.big_coin, small_coin=_db.small_coin,
                      big_coin_amount=_db.big_coin_amount, small_coin_amount=_db.small_coin_amount,
                      trade_threshold=_db.trade_threshold,
                      first_market_api_key=aes_decrypt(_db.first_market_api_key),
                      first_market_api_secret=aes_decrypt(_db.first_market_api_secret),
                      second_market_api_key=aes_decrypt(_db.second_market_api_key),
                      second_market_api_secret=aes_decrypt(_db.second_market_api_secret),
                      status=_db.status,
                      huobi_account=_db.huobi_account, huobipoint_account=_db.huobipoint_account)
            session.commit()
        except:
            session.rollback()
            raise
        return res

    @classmethod
    def fetch_by_id(cls, id):
        """
        获取指定id对应的组合
        :param id:
        :return:
        """
        session = get_dbsession()
        try:
            _db = session.query(CombinationModel).filter_by(id=id).one_or_none()
            if _db is None:
                raise CombinationNotExistError(u'Combination of id {} not exist'.format(id))
            res = cls(id=_db.id, combination=_db.combination, user=_db.user,
                      first_market=_db.first_market, second_market=_db.second_market,
                      big_coin=_db.big_coin, small_coin=_db.small_coin,
                      big_coin_amount=_db.big_coin_amount, small_coin_amount=_db.small_coin_amount,
                      trade_threshold=_db.trade_threshold,
                      first_market_api_key=aes_decrypt(_db.first_market_api_key),
                      first_market_api_secret=aes_decrypt(_db.first_market_api_secret),
                      second_market_api_key=aes_decrypt(_db.second_market_api_key),
                      second_market_api_secret=aes_decrypt(_db.second_market_api_secret),
                      status=_db.status,
                      huobi_account=_db.huobi_account, huobipoint_account=_db.huobipoint_account)
            session.commit()
        except:
            session.rollback()
            raise
        return res

    def add(self):
        session = get_dbsession()
        try:
            session.add(CombinationModel(combination=self.combination, user=self.user,
                                         first_market=self.first_market, second_market=self.second_market,
                                         big_coin=self.big_coin, small_coin=self.small_coin,
                                         big_coin_amount=self.big_coin_amount, small_coin_amount=self.small_coin_amount,
                                         trade_threshold=self.trade_threshold,
                                         first_market_api_key=aes_encrypt(self.first_market_api_key),
                                         first_market_api_secret=aes_encrypt(self.first_market_api_secret),
                                         second_market_api_key=aes_encrypt(self.second_market_api_key),
                                         second_market_api_secret=aes_encrypt(self.second_market_api_secret),
                                         status=self.status,
                                         huobi_account=self.huobi_account, huobipoint_account=self.huobipoint_account))
            session.commit()
        except Exception as e:
            session.rollback()
            print '{}|AddCombinationException|{}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self)
            raise
        obj = self.fetch_by_combination(self.combination)
        self.id = obj.id
        print '{}|AddCombination|{}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), self)
