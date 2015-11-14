#-*-coding:utf-8-*-
from core.mongo import db
from bson.code import Code

def get_member_list(**kwargs):
    results = db.find(kwargs).sort("intercpmem7")

    member_list = []
    for r in results:
        member_list.append(dict(r))
        dict(r)

    return member_list

def get_member_by_contact():
    pass

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
