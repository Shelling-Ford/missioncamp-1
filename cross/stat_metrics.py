'''
통계를 위한 설정파일
'''
METRICS = {
    "basic": {
        '전체': [],
        '개인': [('group_idx', 'none')],
        '단체': [('group_idx', 'not_none')],
        '남': [('sex', 'M')],
        '여': [('sex', 'F')],
        '개인 남': [('sex', 'M'), ('group_idx', 'none')],
        '개인 여': [('sex', 'F'), ('group_idx', 'none')],
        '단체 남': [('sex', 'M'), ('group_idx', 'not_none')],
        '단체 여': [('sex', 'F'), ('group_idx', 'not_none')],
    },
    "group_by": {
        '참가유형별': 'persontype',
        '지부별': 'area_idx',
        '단체별': 'group_idx',
        # '출석교회별': 'church',
    },
    "membership": {
        "cmc": {
            '캠퍼스별': 'campus',
            '전공별': 'major',
            '인터콥 훈련유형별': 'training',
            '직업/직군별': 'job',
        },
        "cbtj": {
            '인터콥 훈련유형별': 'training',
            '직업/직군별': 'job',
            '직장별': 'job_name',
        },
        "ws": {
            '인터콥 훈련유형별': 'training',
            '직분별': 'job',
        },
        "kids": {},
        "youth": {},
    },
}
