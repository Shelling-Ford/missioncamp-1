''' database.py
'''
# pylint: disable=R0903
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

        self.session = scoped_session(sessionmaker(**params))
        self.base = declarative_base()
        self.base.query = self.session.query_property()
        self.base.metadata.create_all(self.engine)


# 인증과 관련해서는 btjkorea의 g5_member테이블을 참조함.
BK_CONF = (config.BKDB_USER, urlquote(config.BKDB_PASSWORD), config.BKDB_HOST)
DB_CONF = (config.DB_USER, urlquote(config.DB_PASSWORD), config.DB_HOST)
BK_URI = "mysql+pymysql://{0}:{1}@{2}/btjkorea?charset=utf8".format(*BK_CONF)
DB_URI = "mysql+pymysql://{0}:{1}@{2}/mcampadm?charset=utf8".format(*DB_CONF)
BTJKOREA_DB = SQLDriver(BK_URI)
DB = SQLDriver(DB_URI)
