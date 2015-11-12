#-*-coding:utf8-*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import collections

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class SQLDriver():
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

        self.Base = declarative_base()
        self.Base.query = self.db_session.query_property()

    # select_all 에 대한 Alias
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
            #rows.append(collections.OrderedDict((col, getattr(row, col)) for col in result._metadata.keys))
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
        r = collections.OrderedDict((col, getattr(row, col)) for col in result._metadata.keys)
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

db = SQLDriver("mysql+mysqldb://root:btj1040!@localhost/mcampadm?charset=utf8")
#intercp_driver = SQLDriver("mssql+pymssql://intercp21:gbs1040@intercp")

from pymongo import MongoClient

class MongoDriver():
    def __init__(self):
        self.client = MongoClient()

    def get_client(self):
        return self.client

def migrate(campcode):
    intercp_driver = SQLDriver("mssql+pymssql://intercp21:gbs1040@intercp")
    results = intercp_driver.select_all("SELECT * FROM %s_member" % campcode)

    for result in results:
        result['campcode'] = campcode

    mongo_driver = MongoDriver()
    mongo_client = mongo_driver.get_client()
    collection = mongo_client.mcamp_old['member']
    collection.insert(results)

    bank_results = intercp_driver.select_all("SELECT * FROM %s_bank" % campcode)

    for result in bank_results:
        collection.update(
            {'campcode': campcode, 'user_id': result['user_id']},
            {'$set': {'bank': result}}
        )

def migrate_all():
    mongo_driver = MongoDriver()
    mongo_client = mongo_driver.get_client()
    collection = mongo_client.mcamp_old['member']
    collection.remove()

    campcodes = [
        'cmc_2008', 'cmc_2009', 'cmc_2010', 'cmc_2011', 'cmc_2011_2', 'cmc_2012', 'cmc_2012_2', 'cmc_2013', 'cmc_2013_2', 'cmc_2014', 'cmc_2014_2', 'cmc_2015_1',
        'ecmc_2013', 'ecmc_2013_2', 'ecmc_2014_2', 'ecmc_2015_1',
        'young_2014', 'young_2014_2', 'young_2015_1',
        'youth_2007', 'youth_2008', 'youth_2009', 'youth_2010', 'youth_2011', 'youth_2011_2', 'youth_2012', 'youth_2012_2', 'youth_2013', 'youth_2013_2', 'youth_2014', 'youth_2014_2', 'youth_2015_1',
        'kids_2007', 'kids_2008', 'kids_2009', 'kids_2010', 'kids_2011', 'kids_2011_2', 'kids_2012', 'kids_2012_2', 'kids_2013', 'kids_2013_2', 'kids_2014', 'kids_2014_2', 'kids_2015_1',
        'ws_2009', 'ws_2010', 'ws_2011', 'ws_2011_2', 'ws_2012', 'ws_2012_2', 'ws_2013', 'ws_2013_2', 'ws_2014', 'ws_2014_2', 'ws_2015_1',
    ]
    for campcode in campcodes:
        migrate(campcode)
        print "%s migrattion done." % campcode
