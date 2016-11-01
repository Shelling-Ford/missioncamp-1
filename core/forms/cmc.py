''' forms.cmc.py
'''
from flask import request
from wtforms import Form, StringField, SelectField, RadioField, PasswordField, HiddenField
from wtforms.widgets import TextArea
from core.models import Area, Camp, Member, Membership
from core.forms import ContactField, MultiCheckboxField
from core.database import db

import datetime
import hashlib

# 직업
jobs = ['정치행정', '법률', '보건의료', '종교', '사회복지', '문화예술스포츠', '정치행정', '경제금융', '연구기술', '교육', '사무관리', '판매서비스', '기계기능', '취업준비', '군인', '기타']

# 통역필요
languages = ['필요없음', '영어', '중국어', '일본어']

# 참가구분
persontypes = ['청년', '대학생', '고3', '스탭']  #상반기 선캠
# persontypes = ['청년', '대학생', '스탭']  # 하반기 선캠

# 인터콥 훈련여부
trainings = [
    ('training1', '비전스쿨'), ('training2', 'BTJ스쿨'), ('training3', '월드미션'), ('training4', '선교캠프'), ('training5', 'MIT'),
    ('training6', 'FO'), ('training7', 'SM'), ('training8', '인터콥캠퍼스'), ('none', '없음')
]


class MemberCommon():
    def populate_membership(self, member_idx):
        if self.getattr('job').data is not None:
            job = Membership()
            job.camp_idx = Camp.get_idx('cmc')
            job.member_idx = member_idx
            job.key = 'job'
            job.value = self.job.data
            db.session.add(job)

        if self.campus.data not in [None, '', 'None']:
            campus = Membership()
            campus.camp_idx = Camp.get_idx('cmc')
            campus.member_idx = member_idx
            campus.key = 'campus'
            campus.value = self.campus.data
            db.session.add(campus)

        if self.major.data not in [None, '', 'None']:
            major = Membership()
            major.camp_idx = Camp.get_idx('cmc')
            major.member_idx = member_idx
            major.key = 'major'
            major.value = self.major.data
            db.session.add(major)

        '''
        if self.sm_yn.data not in [None, '', 'None']:
            sm_yn = Membership()
            sm_yn.camp_idx = Camp.get_idx('cmc')
            sm_yn.member_idx = member_idx
            sm_yn.key = 'sm_yn'
            sm_yn.value = self.sm_yn.data
            db.session.add(sm_yn)
        '''

        if self.vision_yn.data not in [None, '', 'None']:
            vision_yn = Membership()
            vision_yn.camp_idx = Camp.get_idx('cbtj')
            vision_yn.member_idx = member_idx
            vision_yn.key = 'vision_yn'
            vision_yn.value = self.vision_yn.data
            db.session.add(vision_yn)

        if self.training.data not in [None, '', 'None']:
            for training in self.training.data:
                t_membership = Membership()
                t_membership.camp_idx = Camp.get_idx('cmc')
                t_membership.member_idx = member_idx
                t_membership.key = 'training'
                t_membership.value = training
                db.session.add(t_membership)
        db.session.commit()


class RegistrationForm(Form, MemberCommon):
    idx = HiddenField()
    userid = StringField('아이디(이메일)')
    pwd = PasswordField('비밀번호')
    pwd2 = PasswordField('비밀번호 확인')
    name = StringField('이름')
    area_idx = SelectField('지부', choices=Area.get_list('cmc'))
    sex = RadioField('성별', choices=[('M', '남'), ('F', '여')])
    birth = SelectField('출생년도', choices=[("{0}".format(i), "{0}".format(i)) for i in range(2015, 1940, -1)])
    contact = ContactField('연락처')
    church = StringField('소속교회')
    persontype = RadioField('참가구분', choices=[(i, i) for i in persontypes])
    # membership
    job = SelectField('직업/직종', choices=[(i, i) for i in jobs])
    # membership
    campus = StringField('캠퍼스')
    # membership
    major = StringField('전공')
    bus_yn = RadioField('단체버스 이용', choices=[(1, '예'), (0, '아니오')])
    mit_yn = RadioField('2017 겨울 FO/MIT 참가', choices=[(1, '예'), (0, '아니오')])
    fullcamp_yn = RadioField('참가형태', choices=[(1, '전체참가'), (0, '부분참가')])
    date_of_arrival = SelectField('캠프오는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    date_of_leave = SelectField('집에가는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    # membership
    # sm_yn = RadioField('SM(학생선교사) 여부', choices=[(1, '예'), (0, '아니오')])
    newcomer_yn = RadioField('선교캠프가<br/>처음인가요?', choices=[(1, '예'), (0, '아니오')])
    # membership
    vision_yn = RadioField('비전스쿨 수료여부', choices=[(1, '예'), (0, '아니오')])
    # membership
    training = MultiCheckboxField('인터콥 훈련여부', choices=trainings)
    language = SelectField('통역필요', choices=[(i, i) for i in languages])
    memo = StringField('남기고싶은 말', widget=TextArea())

    def set_member_data(self, member):
        membership_data = member.get_membership_data()

        self.idx.data = member.idx
        self.userid.data = member.userid
        self.name.data = member.name
        self.area_idx.data = member.area_idx
        self.sex.data = member.sex
        self.birth.data = member.birth[:4]
        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        self.job.data = membership_data.get('job')
        self.campus.data = membership_data.get('campus')
        self.major.data = membership_data.get('major')
        self.bus_yn.data = member.bus_yn
        self.mit_yn.data = member.mit_yn
        self.fullcamp_yn.data = member.fullcamp_yn
        self.date_of_arrival.data = member.date_of_arrival
        self.date_of_leave.data = member.date_of_leave
        # self.sm_yn.data = membership_data.get('sm_yn')
        self.newcomer_yn.data = member.newcomer_yn
        self.vision_yn.data = int(membership_data.get('vision_yn'))
        self.training.data = membership_data.get('training')
        self.language.data = member.language
        self.memo.data = member.memo

    def populate_obj(self, member):
        member.name = self.name.data
        member.area_idx = self.area_idx.data
        member.contact = request.form.get('hp') + '-' + request.form.get('hp2') + '-' + request.form.get('hp3')
        member.church = self.church.data
        member.birth = self.birth.data
        member.sex = self.sex.data
        member.bus_yn = self.bus_yn.data
        member.mit_yn = self.mit_yn.data
        member.attend_yn = 0
        member.newcomer_yn = self.newcomer_yn.data
        member.persontype = self.persontype.data
        member.fullcamp_yn = self.fullcamp_yn.data
        if self.fullcamp_yn.data == u"1":
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = datetime.datetime.strftime(date_list[0][0], "%Y-%m-%d")
            member.date_of_leave = datetime.datetime.strftime(date_list[-1][0], "%Y-%m-%d")
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.memo = self.memo.data

    def insert(self):
        member = Member()
        member.camp_idx = Camp.get_idx('cmc')
        member.userid = self.userid.data
        member.pwd = hashlib.sha224(self.pwd.data).hexdigest()
        self.populate_obj(member)
        member.group_idx = None
        member.regdate = datetime.datetime.today()
        member.canceldate = None
        member.cancel_yn = 0
        member.cancel_reason = None
        member.room_idx = None
        member.smallgroup_num = None
        db.session.add(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return member.idx

    def update(self, idx):
        member = db.session.query(Member).filter(Member.idx == idx).one()
        db.session.query(Membership).filter(Membership.member_idx == member.idx).delete()
        if self.pwd.data is not None and self.pwd.data != '':
            member.pwd = hashlib.sha224(self.pwd.data).hexdigest()
        self.populate_obj(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return


class GroupMemberRegForm(Form, MemberCommon):
    group_idx = HiddenField()
    name = StringField('이름')
    sex = RadioField('성별', choices=[('M', '남'), ('F', '여')])
    birth = SelectField('출생년도', choices=[("{0}".format(i), "{0}".format(i)) for i in range(2015, 1940, -1)])
    contact = ContactField('연락처')
    church = StringField('소속교회')
    persontype = RadioField('참가구분', choices=[(i, i) for i in persontypes])
    # membership
    job = SelectField('직업/직종', choices=[(i, i) for i in jobs])
    # membership
    campus = StringField('캠퍼스')
    # membership
    major = StringField('전공')
    bus_yn = RadioField('단체버스 이용', choices=[(1, '예'), (0, '아니오')])
    mit_yn = RadioField('2017 겨울 FO/MIT 참가', choices=[(1, '예'), (0, '아니오')])
    fullcamp_yn = RadioField('참가형태', choices=[(1, '전체참가'), (0, '부분참가')])
    date_of_arrival = SelectField('캠프오는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    date_of_leave = SelectField('집에가는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    # membership
    # sm_yn = RadioField('SM(학생선교사) 여부', choices=[(1, '예'), (0, '아니오')])
    newcomer_yn = RadioField('선교캠프가<br/>처음인가요?', choices=[(1, '예'), (0, '아니오')])
    # membership
    vision_yn = RadioField('비전스쿨 수료여부', choices=[(1, '예'), (0, '아니오')])
    # membership
    training = MultiCheckboxField('인터콥 훈련여부', choices=trainings)
    language = SelectField('통역필요', choices=[(i, i) for i in languages])

    def set_member_data(self, member):
        membership_data = member.get_membership_data()

        self.name.data = member.name
        self.sex.data = member.sex
        self.birth.data = member.birth[:4]
        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        self.job.data = membership_data.get('job')
        self.campus.data = membership_data.get('campus')
        self.major.data = membership_data.get('major')
        self.bus_yn.data = member.bus_yn
        self.mit_yn.data = member.mit_yn
        self.fullcamp_yn.data = member.fullcamp_yn
        self.date_of_arrival.data = member.date_of_arrival
        self.date_of_leave.data = member.date_of_leave
        # self.sm_yn.data = membership_data.get('sm_yn')
        self.newcomer_yn.data = member.newcomer_yn
        self.vision_yn.data = int(membership_data.get('vision_yn'))
        self.training.data = membership_data.get('training')
        self.language.data = member.language

    def populate_obj(self, member):
        member.name = self.name.data
        member.contact = request.form.get('hp') + '-' + request.form.get('hp2') + '-' + request.form.get('hp3')
        member.church = self.church.data
        member.birth = self.birth.data
        member.sex = self.sex.data
        member.bus_yn = self.bus_yn.data
        member.mit_yn = self.mit_yn.data
        member.attend_yn = 0
        member.newcomer_yn = self.newcomer_yn.data
        member.persontype = self.persontype.data
        member.fullcamp_yn = self.fullcamp_yn.data
        if self.fullcamp_yn.data == u"1":
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = datetime.datetime.strftime(date_list[0][0], "%Y-%m-%d")
            member.date_of_leave = datetime.datetime.strftime(date_list[-1][0], "%Y-%m-%d")
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data

    def insert(self, group_idx, area_idx):
        member = Member()
        member.camp_idx = Camp.get_idx('cmc')
        member.area_idx = area_idx
        self.populate_obj(member)
        member.group_idx = group_idx
        member.regdate = datetime.datetime.today()
        member.canceldate = None
        member.cancel_yn = 0
        member.cancel_reason = None
        member.room_idx = None
        member.smallgroup_num = None
        db.session.add(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return member.idx

    def update(self, idx):
        member = db.session.query(Member).filter(Member.idx == idx).one()
        db.session.query(Membership).filter(Membership.member_idx == member.idx).delete()
        self.populate_obj(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return
