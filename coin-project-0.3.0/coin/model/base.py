# -*- coding=utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import traceback
try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident
from coin.lib.config import DB, SQL_USER, SQL_PSW


BaseModel = declarative_base()

dbsession_cache = {}
dbsession_used = {}
conf = {
    'url': 'mysql+pymysql://{}:{}@rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com:3306/{}?charset=utf8mb4'.
        format(SQL_USER, SQL_PSW, DB)
}


def create_sqldb_engine(url, options={}):
    kwargs = {
        'pool_size': 3,
        'max_overflow': 0,
        'pool_recycle': 3600
    }
    kwargs.update(options or {})
    return create_engine(url, **kwargs)


def update_dbsession_used(name):
    ident = get_ident()
    used = dbsession_used.setdefault(ident, set())
    used.add(name)


def get_dbsession(name='default'):
    if name not in dbsession_cache:
        engine = create_sqldb_engine(conf['url'], conf.get('options', {}))
        dbsession = scoped_session(sessionmaker(autocommit=False,
                                                autoflush=False, bind=engine))
        dbsession_cache[name] = dbsession
    dbsession_class = dbsession_cache[name]
    update_dbsession_used(name)
    dbsession_class()
    return dbsession_class


def clear_dbsession():
    global dbsession_used
    ident = get_ident()
    dbsessions = dbsession_used.pop(ident, [])
    for name in dbsessions:
        try:
            dbsession_class = dbsession_cache.get(name)
            dbsession_class.remove()
        except:
            print('{}|SqlException|error while clear dbsession|{}'.
                  format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                         traceback.format_exc()))
