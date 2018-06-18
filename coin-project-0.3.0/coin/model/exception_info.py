# -*- coding=utf-8 -*-
"""
记录异常
"""
from sqlalchemy import Column, Index, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, DateTime, TEXT
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class ExceptionInfoModel(BaseModel):

    __tablename__ = 'exception_info'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    host = Column(VARCHAR(64), nullable=False)
    source = Column(VARCHAR(64), nullable=False)
    message = Column(TEXT, nullable=False)
    log_time = Column(DateTime, nullable=False)

    def add(self):
        session = get_dbsession()
        session.add(self)
        session.commit()


Index('exception_info_log_time', ExceptionInfoModel.log_time)


if __name__ == '__main__':
    engine = create_sqldb_engine(conf['url'])
    ExceptionInfoModel.__table__.create(engine)
