# -*- coding=utf-8 -*-
"""
记录Supervisor任务状态
"""
from sqlalchemy import Column, Index, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, DateTime, TEXT
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class SupervisorStatusModel(BaseModel):

    __tablename__ = 'supervisor_status'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    host = Column(VARCHAR(128), nullable=False)
    log_time = Column(TIMESTAMP, nullable=False)
    info = Column(TEXT, nullable=False)

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
    SupervisorStatusModel.__table__.create(engine)
