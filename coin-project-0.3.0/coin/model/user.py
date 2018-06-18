# -*- coding=utf-8 -*-
# -*- coding=utf-8 -*-
from sqlalchemy import Column, Index, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, DateTime
from coin.model.base import BaseModel, conf, create_sqldb_engine, get_dbsession


class UserModel(BaseModel):

    __tablename__ = 'user'

    name = Column(VARCHAR(191), primary_key=True)
    email = Column(VARCHAR(256), nullable=True)

    def add(self):
        session = get_dbsession()
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise

    @classmethod
    def get(cls, name):
        session = get_dbsession()
        return session.query(cls).filter_by(name=name).one_or_none()
