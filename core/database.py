''' database.py
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config


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
        s = self.session()
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
        s = self.session()
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
        s = self.session()
        if params is None:
            s.execute(query)
        else:
            s.execute(query, params)

    def commit(self):
        s = self.session()
        s.commit()


# 인증과 관련해서는 btjkorea의 g5_member테이블을 참조함.
btjkorea_db = SQLDriver("mysql+pymysql://{0}:{1}@{2}/btjkorea?charset=utf8".format(config.bkdb_user, config.bkdb_password, config.bkdb_host))
db = SQLDriver("mysql+pymysql://{0}:{1}@{2}/mcampadm?charset=utf8".format(config.db_user, config.db_password, config.db_host))
