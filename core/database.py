#-*-coding:utf-8-*-
import MySQLdb as mariadb

#conn = mariadb.connect(host='localhost', user='root', passwd='btj1040!', db='mcampadm', charset='utf8')
#cursor = conn.cursor(mariadb.cursors.DictCursor)

def getConnection():
    return mariadb.connect(host='localhost', user='root', passwd='btj1040!', db='mcampadm', charset='utf8')

def getCursor(conn):
    return conn.cursor(mariadb.cursors.DictCursor)


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqldb://root:btj1040!@localhost/mcampadm?charset=utf8')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import models
    Base.metadata.create_all(bind=engine)

import collections
#
# 쿼리문을 넘겨주면 실행 후 dictionary 리스트를 반환해줌
# param: query string, return: list of dictionary obj
def execute(query, params=None):
    s = db_session()
    if params is None:
        result = s.execute(query)
    else:
        result = s.execute(query, params)
    row = result.fetchone()
    rows = []
    while row is not None:
        rows.append(collections.OrderedDict((col, getattr(row, col)) for col in result._metadata.keys))
        row = result.fetchone()

    return rows

def select_one(query, params=None):
    s = db_session()
    if params is None:
        result = s.execute(query)
    else:
        result = s.execute(query, params)
    row = result.fetchone()
    collections.OrderedDict((col, getattr(row, col)) for col in result._metadata.keys)
    return row

def raw_query(query, params=None):
    s = db_session()
    if params is None:
        s.execute(query)
    else:
        s.execute(query, params)

def commit():
    s = db_session()
    s.commit()
