''' database.py
'''
from urllib.parse import quote_plus as urlquote
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config


class SQLDriver():
    ''' SQLAlchemy 데이터베이스 드라이버를 초기화해줌.
    '''
    def __init__(self, uri):
        ''' 초기화 함수
        '''
        self.engine = create_engine(uri)
        params = {
            "autocommit": False,
            "autoflush": False,
            "bind": self.engine
        }
        self.db_session = scoped_session(sessionmaker(**params))
        self.session = self.db_session

        self.base = declarative_base()
        self.base.query = self.db_session.query_property()
        self.base.metadata.create_all(self.engine)

    # select_all 에 대한 Alias @deprecated
    def execute(self, query, params=None):
        ''' select 쿼리를 실행하여 모든 row를 반환함
            반환 형식은 Dictionary
        '''
        return self.select_all(query, params)

    def select_all(self, query, params=None):
        ''' select 쿼리를 실행하여 모든 row를 반환함
            반환 형식은 Dictionary
        '''
        session = self.session()
        if params is None:
            result = session.execute(query)
        else:
            result = session.execute(query, params)
        row = result.fetchone()
        rows = []
        while row is not None:
            row_dict = dict()
            for col in result._metadata.keys:
                row_dict[col] = getattr(row, col)
            rows.append(row_dict)
            row = result.fetchone()

        return rows

    def select_one(self, query, params=None):
        ''' select 쿼리를 실행하여 첫 번째 row를 반환해줌.
            반환 형식은 Dictionary
        '''
        session = self.session()
        if params is None:
            result = session.execute(query)
        else:
            result = session.execute(query, params)
        row = result.fetchone()
        if row is not None:
            row_dict = dict((col, getattr(row, col)) for col in result._metadata.keys)
        else:
            row_dict = None

        return row_dict

    def raw_query(self, query, params=None):
        ''' insert나 update처럼 결과값을 반환하지 않는 쿼리를 실행할 때 사용하는 함수
        '''
        session = self.session()
        if params is None:
            session.execute(query)
        else:
            session.execute(query, params)

    def commit(self):
        ''' 쿼리 실행 결과를 커밋함.
        '''
        session = self.session()
        session.commit()


# 인증과 관련해서는 btjkorea의 g5_member테이블을 참조함.
BK_CONF = (config.BKDB_USER, urlquote(config.BKDB_PASSWORD), config.BKDB_HOST)
DB_CONF = (config.DB_USER, urlquote(config.DB_PASSWORD), config.DB_HOST)
BK_URI = "mysql+pymysql://{0}:{1}@{2}/btjkorea?charset=utf8".format(*BK_CONF)
DB_URI = "mysql+pymysql://{0}:{1}@{2}/mcampadm?charset=utf8".format(*DB_CONF)
BTJKOREA_DB = SQLDriver(BK_URI)
DB = SQLDriver(DB_URI)
