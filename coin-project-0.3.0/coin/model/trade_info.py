# -*- coding=utf-8 -*-
from sqlalchemy import Column, Index, BIGINT, VARCHAR, DateTime, DECIMAL, Text, TIMESTAMP
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class TradeInfoModel(BaseModel):

    __tablename__ = 'market_trade_info'

    trade_pair_id = Column(VARCHAR(64), primary_key=True)
    account_id = Column(VARCHAR(64), primary_key=True)
    market = Column(VARCHAR(64), primary_key=True)
    combination = Column(VARCHAR(128), nullable=False)
    order_id = Column(BIGINT, nullable=True, default=None)
    state = Column(VARCHAR(64), nullable=False)
    symbol = Column(VARCHAR(32), nullable=False)
    trade_side = Column(VARCHAR(32), nullable=False)
    trade_target = Column(VARCHAR(64), nullable=True)
    create_time = Column(DateTime, nullable=False)
    finish_time = Column(BIGINT, nullable=True, default=None)
    query_amount = Column(DECIMAL(30, 10), nullable=False)
    query_price = Column(DECIMAL(30, 10), nullable=False)
    depth = Column(Text, nullable=True)
    filled_amount = Column(DECIMAL(30, 10), nullable=True)
    filled_fees = Column(DECIMAL(30, 10), nullable=True)  # 手续费
    exception_message = Column(Text, nullable=True)

    def add(self):
        session = get_dbsession()
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise


Index('trade_create_time', TradeInfoModel.create_time)
Index('trade_order_id', TradeInfoModel.order_id)


class CombinationTradeInfoModel(BaseModel):

    __tablename__ = 'combination_trade_info'

    combination = Column(VARCHAR(128), primary_key=True)
    trade_pair_id = Column(VARCHAR(64), primary_key=True)
    market = Column(VARCHAR(64), primary_key=True)
    order_id = Column(BIGINT, nullable=True, default=None)
    order_time = Column(TIMESTAMP(3), nullable=True)
    state = Column(VARCHAR(64), nullable=False)
    symbol = Column(VARCHAR(32), nullable=False)
    trade_side = Column(VARCHAR(32), nullable=False)
    trade_target = Column(VARCHAR(64), nullable=True)
    create_time = Column(TIMESTAMP(3), nullable=False)
    query_amount = Column(DECIMAL(30, 10), nullable=False)
    query_price = Column(DECIMAL(30, 10), nullable=False)
    depth = Column(Text, nullable=True)
    depth_time = Column(TIMESTAMP(3), nullable=False)
    filled_amount = Column(DECIMAL(30, 10), nullable=True)
    filled_fees = Column(DECIMAL(30, 10), nullable=True)  # 手续费
    exception_message = Column(Text, nullable=True)

    def add(self):
        session = get_dbsession()
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise


Index('combination_trade_create_time', CombinationTradeInfoModel.create_time)
Index('combination_trade_order_id', CombinationTradeInfoModel.order_id)


if __name__ == '__main__':
    engine = create_sqldb_engine(conf['url'])
    CombinationTradeInfoModel.__table__.create(engine)
