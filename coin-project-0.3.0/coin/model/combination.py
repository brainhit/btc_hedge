# -*- coding=utf-8 -*-
from sqlalchemy import Column, Index, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, DateTime
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class CombinationModel(BaseModel):

    __tablename__ = 'trade_combination'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    combination = Column(VARCHAR(191), nullable=False, unique=True)
    user = Column(VARCHAR(256), nullable=False)
    first_market = Column(VARCHAR(256), nullable=False)
    second_market = Column(VARCHAR(256), nullable=False)
    big_coin = Column(VARCHAR(256), nullable=False)
    small_coin = Column(VARCHAR(256), nullable=False)
    big_coin_amount = Column(DECIMAL(30, 10), nullable=False)
    small_coin_amount = Column(DECIMAL(30, 10), nullable=False)
    trade_threshold = Column(DECIMAL(30, 10), nullable=False)  # 触发交易的比例
    first_market_api_key = Column(VARCHAR(256), nullable=False)
    first_market_api_secret = Column(VARCHAR(256), nullable=False)
    second_market_api_key = Column(VARCHAR(256), nullable=False)
    second_market_api_secret = Column(VARCHAR(256), nullable=False)
    status = Column(VARCHAR(32), nullable=False, default='Active')
    huobi_account = Column(BIGINT, nullable=True)  # 只有火币账号需要该信息
    huobipoint_account = Column(BIGINT, nullable=True)

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
    CombinationModel.__table__.create(engine)
