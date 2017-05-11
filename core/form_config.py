''' Camp specific form configuration file
'''

JOBS = [
    '경영·사무', '영업·고객상담', '생산·제조', 'IT·인터넷', '전문직', '교육', '의료', '미디어',
    '공무원', '건설', '유통·무역', '서비스', '디자인', '취업준비', '군인', '기타'
]
CHURCH_JOBS = [
    '목회자', '장로', '권사', '집사', '성도', '청년'
]
LANGUAGES = ['필요없음', '영어', '중국어', '일본어']
PERSONTYPES = {
    'cbtj': ['청년', '스탭'],
    'cmc': ['청년', '대학생', '스탭'],
    'kids': [
        '어린이', '교사', '교역자', '예배팀''키즈스탭', '유스탭',
        '선캠팀장', '중보스탭', '캠프스탭', '기쁜맘', '선교사', 'MIT', 'MIT교사', '기타'
    ],
    'ws': ['일반', '어린이', '키즈', '중보방', '전일스탭(2박3일)'],
    'youth': ['중학생', '고등학생', '교사', '교역자', '기타'],
}
TRAININGS = {
    'cbtj': [
        ('training1', '비전스쿨'), ('training2', 'BTJ스쿨'),
        ('training3', '월드미션'), ('training4', '선교캠프'),
        ('training5', 'MIT'),
        ('training6', 'FO'), ('training7', 'C-BTJ'),
        ('training8', 'Y-Tentmaker'), ('training9', 'SM'),
        ('training10', '기타'), ('none', '없음')
    ],
    'cmc': [
        ('training1', '비전스쿨'), ('training2', 'BTJ스쿨'),
        ('training3', '월드미션'), ('training4', '선교캠프'),
        ('training5', 'MIT'),
        ('training6', 'FO'), ('training7', 'SM'),
        ('training8', '인터콥캠퍼스'), ('none', '없음')
    ],
    'kids': [
        ('training1', '어린이비전스쿨'), ('training2', '월드미션'),
        ('training3', '선교캠프'), ('training4', 'MIT'), ('none', '없음')
    ],
    'ws': [
        ('training1', '시니어비전스쿨'), ('training2', '여성비전스쿨'),
        ('training3', '목회자비전스쿨'), ('training4', '비전스쿨'),
        ('training5', '월드미션'),
        ('training6', 'FO'), ('training7', '선교캠프'),
        ('training8', '어린이/키즈 선교캠프'), ('none', '없음')
    ],
    'youth': [
        ('training1', '청소년비전스쿨'), ('training2', 'Mission Academy'),
        ('training3', 'U★BTJ Club School'), ('training4', 'UGLC'),
        ('training5', '청소년월드미션'),
        ('training6', '청소년선교캠프'), ('training7', '청소년MIT,GUMF'),
        ('training8', 'U★BTJ 운동가'), ('none', '없음')
    ],
}
ROUTES = {
    'youth': [
        ('route1', "지인추천(친구,선생님)"), ('route2', "교회추천"),
        ('route3', "홍보물(포스터,브로셔)"), ('route4', "인터넷(Facebook,포털사이트,카페 등등)"),
        ('route5', "월드미션"), ('route6', "유비투어"),
        ('route6', "U★BTJ"), ('none', '없음')
    ]
}
MEMBERSHIP_FIELDS = {
    'cbtj': ['job', 'job_name', 'vision_yn'],
    'cmc': ['job', 'campus', 'major', 'vision_yn'],
    'kids': ['pname', 'sch1', 'sch2'],
    'ws': ['job', 'pname', 'stafftype'],
    'youth': ['sch1', 'sch2'],
    'ga': ['enname', 'etcperson', 'pname', 'address', 'location', 'city', 'etclanguage', 'route', 'denomination'],
}
GROUP_TYPES = {
    'youth': [
        ('1', '다니엘과 세친구'), ('2', '예수님과 열두제자'), ('3', '단체교회')
    ]
}
STAFF_TYPES = {
    'ws': [
        ("(전일)식당스탭", "(전일)식당스탭"),
        ("(전일)조리스탭", "(전일)조리스탭"),
        ("내부안내", "내부안내"),
        ("로비", "로비"),
        ("차량", "차량"),
        ("어린이스탭", "어린이스탭"),
        ("키즈스탭", "키즈스탭"),
        ("판매스탭", "판매스탭"),
        ("기타", """기타
        <span style='color:red; font-size:9px;'>
        (**위의 스텝에 해당되지 않는경우 남기고 싶은 말에 남겨 주세요)
        </span>
        """)
    ]
}
SCH2_CHOICES = {
    'kids': [
        ('예비1학년', '예비1학년'),
        *[("{0}학년".format(i), "{0}학년".format(i)) for i in range(1, 7)]
    ],
    'youth': [("{0}학년".format(i), "{0}학년".format(i)) for i in range(1, 4)]
}
