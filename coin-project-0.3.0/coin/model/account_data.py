# -*- coding=utf-8 -*-
"""
货币和点卡数据
"""
from sqlalchemy import Column, Index, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, DateTime
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class AccountDataModel(BaseModel):

    __tablename__ = 'market_coin_data'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    huobi_btc = Column(DECIMAL(30, 10), nullable=False)
    binance_btc = Column(DECIMAL(30, 10), nullable=False)
    huobi_iost = Column(DECIMAL(30, 10), nullable=False)
    binance_iost = Column(DECIMAL(30, 10), nullable=False)
    btc_total = Column(DECIMAL(30, 10), nullable=False)
    iost_total = Column(DECIMAL(30, 10), nullable=False)
    bnb = Column(DECIMAL(30, 10), nullable=False)
    huobi_point = Column(DECIMAL(30, 10), nullable=False)
    price = Column(DECIMAL(30, 10), nullable=False)
    log_time = Column(DateTime, nullable=False)

    def add(self):
        session = get_dbsession()
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise


Index('account_data_log_time', AccountDataModel.log_time)


class AccountCoinInfoModel(BaseModel):

    __tablename__ = 'coin_info'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    combination = Column(VARCHAR(191), nullable=False)
    first_market_big_coin = Column(DECIMAL(30, 10), nullable=False)
    first_market_small_coin = Column(DECIMAL(30, 10), nullable=False)
    second_market_big_coin = Column(DECIMAL(30, 10), nullable=False)
    second_market_small_coin = Column(DECIMAL(30, 10), nullable=False)
    big_coin_total = Column(DECIMAL(30, 10), nullable=False)
    small_coin_total = Column(DECIMAL(30, 10), nullable=False)
    bnb = Column(DECIMAL(30, 10), nullable=False)
    huobi_point = Column(DECIMAL(30, 10), nullable=False)
    symbol_price = Column(DECIMAL(30, 10), nullable=False)
    bnb_price = Column(DECIMAL(30, 10), nullable=False)
    btc_price = Column(DECIMAL(30, 10), nullable=False)
    status = Column(VARCHAR(32), nullable=False, default='Active')
    big_coin_btc_price = Column(DECIMAL(30, 10), nullable=True)  # 大币到BTC的价格
    log_time = Column(DateTime, nullable=False)

    def add(self):
        session = get_dbsession()
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise


if __name__ == '__main__':
    engine = create_sqldb_engine(conf['url'])
    AccountCoinInfoModel.__table__.create(engine)
