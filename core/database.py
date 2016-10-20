# -*-coding:utf8-*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# import collections

import sys
reload(sys)
sys.setdefaultencoding('utf8')


class SQLDriver():
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.session = self.db_session

        self.Base = declarative_base()
        self.Base.query = self.db_session.query_property()

    # select_all 에 대한 Alias @deprecated
    def execute(self, query, params=None):
        return self.select_all(query, params)

    def select_all(self, query, params=None):
        s = self.db_session()
        if params is None:
            result = s.execute(query)
        else:
            result = s.execute(query, params)
        row = result.fetchone()
        rows = []
        while row is not None:
            # rows.append(collections.OrderedDict((col, getattr(row, col)) for col in result._metadata.keys))
            rows.append(dict((col, getattr(row, col)) for col in result._metadata.keys))
            row = result.fetchone()

        return rows

    def select_one(self, query, params=None):
        s = self.db_session()
        if params is None:
            result = s.execute(query)
        else:
            result = s.execute(query, params)
        row = result.fetchone()
        if row is not None:
            r = dict((col, getattr(row, col)) for col in result._metadata.keys)
        else:
            r = None

        return r

    def raw_query(self, query, params=None):
        s = self.db_session()
        if params is None:
            s.execute(query)
        else:
            s.execute(query, params)

    def commit(self):
        s = self.db_session()
        s.commit()


# 인증과 관련해서는 btjkorea의 g5_member테이블을 참조함.
# btjkorea_db = SQLDriver("mysql+pymysql://btjkorea:qlxlwpdl1040!@localhost/btjkorea?charset=utf8")

db = SQLDriver("mysql+pymysql://root:btj1040!@localhost/mcampadm?charset=utf8")
# intercp_driver = SQLDriver("mssql+pymssql://intercp21:gbs1040@intercp")
