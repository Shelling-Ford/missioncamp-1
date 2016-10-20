#-*-coding:utf-8-*-
from core.mongo import db, call_log
from core.models import Member
from bson.code import Code

def get_member_list(**kwargs):
    params = dict()

    # skip = kwargs['skip'] if 'skip' in kwargs and kwargs['skip'] != None else 0
    keys = ['campcode', 'area', 'name', 'camp', 'hp1']
    for k in keys:
        if k in kwargs and kwargs[k] is not None:
            params[k] = kwargs[k]

    params['fin'] = {"$ne":"d"}

    results = db.find(params).sort("regday",1)
    member_list = [dict(r) for r in results]
    return member_list

# 선캠 참석횟수와 함께 리턴
def get_member_list_with_count(**kwargs):
    params = dict()

    skip = kwargs['skip'] if 'skip' in kwargs else 0
    print skip

    keys = ['campcode', 'area', 'name', 'camp']
    for k in keys:
        if k in kwargs and kwargs[k] is not None:
            params[k] = kwargs[k]

    params['fin'] = {"$ne":"d"}

    if('campcode' in kwargs and kwargs['campcode'] is not None and kwargs['campcode'].split('_')[0] == 'youth'):
        params['ssn'] = {"$regex":r"^97[0-9]*$"}

    results = db.find(params)

    if('campcode' in kwargs and kwargs['campcode'] is not None and kwargs['campcode'].split('_')[0] == 'cmc'):
        results = results.sort("intercpmem7")
    elif('campcode' in kwargs and kwargs['campcode'] is not None and kwargs['campcode'].split('_')[0] == 'youth'):
        results = results.sort("ssn", -1)

    if skip is not None and skip != 0:
        results = results.skip(skip).limit(50)

    member_list = []
    for r in results:
        item = dict(r)
        count = Member.count(name=item['name'], contact=item['hp1'], attend_yn=1, cancel_yn=0)
        count += db.count({"hp1": item["hp1"], "name":item["name"], "entry":"Y", "fin":{"$ne":"d"}})
        item['count'] = count
        item['call_count'] = call_log.count({"name":item["name"], "hp1":item["hp1"]})
        member_list.append(item)

    return member_list

def get_member_count(**kwargs):
    params = dict()

    keys = ['campcode', 'area', 'name', 'camp']
    for k in keys:
        if k in kwargs and kwargs[k] is not None:
            params[k] = kwargs[k]

    params['fin'] = {"$ne":"d"}

    if('campcode' in kwargs and kwargs['campcode'] is not None and kwargs['campcode'].split('_')[0] == 'youth'):
        params['ssn'] = {"$regex":r"^97[0-9]*$"}

    count = db.count(params)
    return count

def get_member_call_logs(name, hp1):
    params = {"name":name, "hp1":hp1}
    results = call_log.find(params)
    logs = [i for i in results]

    return logs

def get_member_call_log_count(name, hp1):
    params = {"name":name, "hp1":hp1}
    count = call_log.count(params)
    return count

def save_member_call_log(name, hp1, date, log):
    params = {"name":name, "hp1":hp1, "date":date, "log":log}
    call_log.insert(params)

def get_basic_stat(campcode):
    summary = []

    total = db.aggregate(
        [
            {"$match":{"campcode":campcode, "fin":{"$ne":"d"}}},
            {"$group":{
                "_id":"null",
                "cnt":{"$sum": 1},
                "r_cnt":{"$sum":{"$cond":[{"$eq":["$bank.bankname", "Y"]}, 1, 0]}},
                "a_cnt":{"$sum":{"$cond":[{"$eq":["$entry","Y"]}, 1, 0]}}
            }},
            {"$project":{
                "name":"$_id",
                "cnt":1,
                "r_cnt":1,
                "a_cnt":1,
            }},
        ]
    ).next()
    total['name'] =u'전체'
    summary.append(total)

    individual = db.aggregate(
        [
            {"$match":{"campcode":campcode, "fin":{"$ne":"d"}, "corpidx":{"$eq":0}}},
            {"$group":{
                "_id":"null",
                "cnt":{"$sum": 1},
                "r_cnt":{"$sum":{"$cond":[{"$eq":["$bank.bankname", "Y"]}, 1, 0]}},
                "a_cnt":{"$sum":{"$cond":[{"$eq":["$entry","Y"]}, 1, 0]}}
            }},
            {"$project":{
                "name":"$_id",
                "cnt":1,
                "r_cnt":1,
                "a_cnt":1,
            }},
        ]
    ).next()
    individual['name'] = u'개인'
    summary.append(individual)

    group = db.aggregate(
        [
            {"$match":{"campcode":campcode, "fin":{"$ne":"d"}, "corpidx":{"$ne":0}}},
            {"$group":{
                "_id":"null",
                "cnt":{"$sum": 1},
                "r_cnt":{"$sum":{"$cond":[{"$eq":["$bank.bankname", "Y"]}, 1, 0]}},
                "a_cnt":{"$sum":{"$cond":[{"$eq":["$entry","Y"]}, 1, 0]}}
            }},
            {"$project":{
                "name":"$_id",
                "cnt":1,
                "r_cnt":1,
                "a_cnt":1,
            }},
        ]
    ).next()
    group['name'] = u'단체'
    summary.append(group)

    by_sex = db.aggregate(
        [
            {"$match":{"campcode":campcode, "fin":{"$ne":"d"}}},
            {"$group":{
                "_id":{"$cond":[{"$eq":["$sex", "M"]}, u"남", {"$cond":[{"$eq":["$sex", "F"]}, u"여", u"오류"]}]},
                "cnt":{"$sum": 1},
                "r_cnt":{"$sum":{"$cond":[{"$eq":["$bank.bankname", "Y"]}, 1, 0]}},
                "a_cnt":{"$sum":{"$cond":[{"$eq":["$entry","Y"]}, 1, 0]}}
            }},
            {"$project":{
                "name":"$_id",
                "cnt":1,
                "r_cnt":1,
                "a_cnt":1,
            }},
        ]
    )

    for d in by_sex:
        summary.append(d)

    stat = dict()
    stat['summary'] = summary
    stat['area'] = db.aggregate(
        [
            {"$match":{"campcode":campcode, "fin":{"$ne":"d"}}},
            {"$group":{
                "_id":"$area",
                "cnt":{"$sum": 1},
                "r_cnt":{"$sum":{"$cond":[{"$eq":["$bank.bankname", "Y"]}, 1, 0]}},
                "a_cnt":{"$sum":{"$cond":[{"$eq":["$entry","Y"]}, 1, 0]}}
            }},
            {"$project":{
                "name":"$_id",
                "cnt":1,
                "r_cnt":1,
                "a_cnt":1,
            }},
        ]
    )
    return stat