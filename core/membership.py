# -*-coding:utf-8-*-
''' deprecated
    삭제예정
'''
memberships = [
    {
        'name': 'job',
        'condition': [
            {'persontype': u'청년', 'camp_idx': getCampIdx('cmc')},
            {'persontype': u'청년', 'camp_idx': getCampIdx('cbtj')},
            {'persontype': u'일반', 'camp_idx': getCampIdx('ws')}
        ]
    },
    {
        'name': 'sch1',
        'condition': [
            {'persontype': u'대학생', 'camp_idx': getCampIdx('cmc')},
            {'persontype': u'청소년', 'camp_idx': getCampIdx('youth')},
            {'persontype': u'어린이', 'camp_idx': getCampIdx('kids')},
        ]
    },
    {
        'name': 'sch2',
        'condition': [
            {'persontype': u'대학생', 'camp_idx': getCampIdx('cmc')},
            {'persontype': u'청소년', 'camp_idx': getCampIdx('youth')},
            {'persontype': u'어린이', 'camp_idx': getCampIdx('kids')},
        ]
    },
    {
        'name': 'stafftype',
        'condition': [
            {'persontype': u'전일스탭', 'camp_idx': getCampIdx('ws')},
            {'persontype': u'스탭', 'camp_idx': getCampIdx('kids')},
        ]
    },
    {
        'name': 'pname',
        'condition': [
            {'persontype': u'어린이', 'camp_idx': getCampIdx('ws')},
            {'persontype': u'키즈', 'camp_idx': getCampIdx('ws')},
        ]
    },
    {'name': 'training'},
    {
        'name': 'route',
        'condition': [
            {'persontype': u'청소년', 'camp_idx': getCampIdx('youth')}
        ]
    },
    {
        'name': 'pcontact',
        'condition': [
            {'persontype': u'청소년', 'camp_idx': getCampIdx('youth')}
        ]
    },
    {
        'name': 'mcontact',
        'condition': [
            {'persontype': u'청소년', 'camp_idx': getCampIdx('youth')}
        ]
    },
    {
        'name': 'foreigner',
        'condition': [
            {'persontype': u'대학생', 'camp_idx': getCampIdx('cmc')},
            {'persontype': u'청년', 'camp_idx': getCampIdx('cmc')},
        ]
    },
    {
        'name': 'nationality',
        'condition': [
            {'persontype': u'대학생', 'camp_idx': getCampIdx('cmc')},
            {'persontype': u'청년', 'camp_idx': getCampIdx('cmc')},
        ]
    },
]
