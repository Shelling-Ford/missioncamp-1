
from pymongo import MongoClient
from core.database import SQLDriver

class MongoDriver():
    def __init__(self):
        self.client = MongoClient()

    def get_client(self):
        return self.client

driver = MongoDriver()
client = driver.get_client()
db = client.mcamp_old.member
call_log = client.mcamp_old.call_log

def migrate(campcode):
    mongo_driver = MongoDriver()
    mongo_client = mongo_driver.get_client()
    member = mongo_client.mcamp_old['member']

    count = member.count({'campcode':campcode})
    if count == 0:
        intercp_driver = SQLDriver("mssql+pymssql://intercp21:gbs1040@intercp")
        results = intercp_driver.select_all("SELECT * FROM %s_member" % campcode)

        for result in results:
            result['campcode'] = campcode

        if results is not None and len(results) > 0:
            member.insert(results)
        else:
            print('%s not found.' % campcode)

        bank_results = intercp_driver.select_all("SELECT * FROM %s_bank" % campcode)

        for result in bank_results:
            member.update(
                {'campcode': campcode, 'user_id': result['user_id']},
                {'$set': {'bank': result}}
            )

        print("%s migration done." % campcode)

def migrate_all():
    mongo_driver = MongoDriver()
    mongo_client = mongo_driver.get_client()
    member = mongo_client.mcamp_old['member']

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
