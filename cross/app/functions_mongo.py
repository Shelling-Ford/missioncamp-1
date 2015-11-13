#-*-coding:utf-8-*-
from core.mongo import db

def get_member_list(**kwargs):
    results = db.find(kwargs).sort("intercpmem7")

    member_list = []
    for r in results:
        member_list.append(dict(r))
        dict(r)

    return member_list

def get_member_by_contact():
    results = db.aggregate(
        [


            {
                "$group": {
                    "_id": {"name": "$name", "hp1":"$hp1"},
                    "campcode": "$campcode",
                    "intercpmem7": {"$max":"$intercpmem7"},
                    "count": {"$sum": 1}
                }

            },

            {
                "$match": {
                    "$or": [
                        {"campcode":"cmc_2015_1"},
                        {"campcode":"cmc_2014"},
                        {"campcode":"cmc_2014_2"},
                    ]
                }
            },
        ]
    )

    member_list = []
    for r in results:
        member_list.append(dict(r))
        dict(r)

    return member_list
