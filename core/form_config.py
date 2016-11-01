''' Camp specific form configuration file
'''

JOBS = [
    '정치행정', '법률', '보건의료', '종교', '사회복지', '문화예술스포츠', '정치행정', '경제금융',
    '연구기술', '교육', '사무관리', '판매서비스', '기계기능', '취업준비', '군인', '기타'
]
LANGUAGES = ['필요없음', '영어', '중국어', '일본어']
PERSONTYPES = {
    'cmc': ['청년', '대학생', '고3', '스탭'],
    'cbtj': ['청년', '스탭'],
}
TRAININGS = {
    'cmc': [
        ('training1', '비전스쿨'), ('training2', 'BTJ스쿨'),
        ('training3', '월드미션'), ('training4', '선교캠프'),
        ('training5', 'MIT'),
        ('training6', 'FO'), ('training7', 'SM'),
        ('training8', '인터콥캠퍼스'), ('none', '없음')
    ],
    'cbtj': [
        ('training1', '비전스쿨'), ('training2', 'BTJ스쿨'),
        ('training3', '월드미션'), ('training4', '선교캠프'),
        ('training5', 'MIT'),
        ('training6', 'FO'), ('training7', 'C-BTJ'),
        ('training8', 'Y-Tentmaker'), ('training9', 'SM'),
        ('training10', '기타'), ('none', '없음')
    ],
}
MEMBERSHIP_FIELDS = {
    'cmc': [
        'job', 'campus', 'major', 'vision_yn'
    ]
}
GROUP_TYPES = {
    'youth': [
        ('1', '다니엘과 세친구'), ('2', '예수님과 열두제자'), ('3', '단체교회')
    ]
}
