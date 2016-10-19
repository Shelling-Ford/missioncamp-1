# -*-coding:utf-8-*-
from flask import request
from wtforms import Form, StringField, SelectField, RadioField, PasswordField, HiddenField
from wtforms.widgets import TextArea
from core.models import Area, Camp, Member, Membership
from core.forms import ContactField, MultiCheckboxField
from core.database import db

import datetime

# 직업
jobs = []

# 통역필요
languages = []

# 참가구분
persontypes = []


class RegistrationForm(Form):
    idx = HiddenField()
    camp_idx = HiddenField()
    userid = StringField(u'아이디')
    pwd = PasswordField(u'비밀번호')
    pwd2 = PasswordField(u'비밀번호 확인')
    name = StringField(u'이름')
    area_idx = SelectField(u'지부', choices=Area.get_list('cmc'))
    sex = RadioField(u'성별', choices=[('M', u'남'), ('F', u'여')])
    birth = SelectField(u'출생년도', choices=[(unicode(i), unicode(i)) for i in range(2015, 1940, -1)])
    contact = ContactField(u'연락처')
    church = StringField(u'소속교회')
    persontype = RadioField(u'참가구분', choices=[(u'청년', u'청년'), (u'대학생', u'대학생'), (u'고3', u'고3'), (u'스탭', u'청년/대학생스탭')])
    # membership
    job = SelectField(
        u'직업/직종',
        choices=[
            (u'정치행정', u'정치행정'), (u'법률', u'법률'), (u'보건의료', u'보건의료'), (u'종교', u'종교'), (u'사회복지', u'사회복지'),
            (u'문화예술스포츠', u'문화예술스포츠'), (u'정치행정', u'정치행정'), (u'경제금융', u'경제금융'), (u'연구기술', u'연구기술'), (u'교육', u'교육'),
            (u'사무관리', u'사무관리'), (u'판매서비스', u'판매서비스'), (u'기곅능', u'기계기능'), (u'취업준비', u'취업준비'), (u'군인', u'군인'), (u'기타', u'기타'),
        ]
    )
    # membership
    campus = StringField(u'캠퍼스')
    # membership
    major = StringField(u'전공')
    bus_yn = RadioField(u'단체버스 이용', choices=[(1, u'예'), (0, u'아니오')])
    mit_yn = RadioField(u'FO/MIT 참가', choices=[(1, u'예'), (0, u'아니오')])
    fullcamp_yn = RadioField(u'참가형태', choices=[(1, u'전체참가'), (0, u'부분참가')])
    date_of_arrival = SelectField(u'캠프오는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    date_of_leave = SelectField(u'집에가는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    # membership
    sm_yn = RadioField(u'SM(학생선교사) 여부', choices=[(1, u'예'), (0, u'아니오')])
    newcomer_yn = RadioField(u'선교캠프가<br/>처음인가요?', choices=[(1, u'예'), (0, u'아니오')])
    # membership
    training = MultiCheckboxField(
        u'인터콥 훈련여부',
        choices=[
            ('training1', u'비전스쿨'), ('training2', u'BTJ스쿨'), ('training3', u'월드미션'), ('training4', u'선교캠프'), ('training5', u'MIT'),
            ('training6', u'FO'), ('training7', u'SM'), ('training8', u'인터콥캠퍼스'), ('none', u'없음')
        ]
    )
    language = SelectField(u'통역필요', choices=[(u'필요없음', u'필요없음'), (u'영어', u'영어'), (u'중국어', u'중국어'), (u'일본어', u'일본어')])
    memo = StringField(u'남기고싶은 말', widget=TextArea())

    def set_member_data(self, member):
        membership_data = member.get_membership_data()

        self.idx.data = member.idx
        self.camp_idx.data = member.camp_idx
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
        self.sm_yn.data = membership_data.get('sm_yn')
        self.newcomer_yn.data = member.newcomer_yn
        self.training.data = membership_data.get('training')
        self.language.data = member.language
        self.memo.data = member.memo

    def populate_obj(self, member):
        member.camp_idx = Camp.get_idx('cmc')
        member.userid = self.userid.data
        member.pwd = self.pwd.data
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
        if self.fullcamp_yn.data == 1:
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = datetime.datetime.strftime(date_list[0][0], "%Y-%m-%d")
            member.date_of_leave = datetime.datetime.strftime(date_list[-1][0], "%Y-%m-%d")
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.group_idx = None
        member.regdate = datetime.datetime.today()
        member.canceldate = None
        member.cancel_yn = 0
        member.cancel_reason = None
        member.memo = self.memo.data
        member.room_idx = None
        member.smallgroup_num = None

    def populate_membership(self, member_idx):
        if self.job.data is not None:
            job = Membership()
            job.camp_idx = Camp.get_idx('cmc')
            job.member_idx = member_idx
            job.key = 'job'
            job.value = self.job.data
            db.session.add(job)

        if self.campus.data is not None:
            campus = Membership()
            campus.camp_idx = Camp.get_idx('cmc')
            campus.member_idx = member_idx
            campus.key = 'campus'
            campus.value = self.campus.data
            db.session.add(campus)

        if self.major.data is not None:
            major = Membership()
            major.camp_idx = Camp.get_idx('cmc')
            major.member_idx = member_idx
            major.key = 'major'
            major.value = self.major.data
            db.session.add(major)

        if self.sm_yn.data is not None:
            sm_yn = Membership()
            sm_yn.camp_idx = Camp.get_idx('cmc')
            sm_yn.member_idx = member_idx
            sm_yn.key = 'sm_yn'
            sm_yn.value = self.sm_yn.data
            db.session.add(sm_yn)

        if self.training.data is not None:
            for training in self.training.data:
                t_membership = Membership()
                t_membership.camp_idx = Camp.get_idx('cmc')
                t_membership.member_idx = member_idx
                t_membership.key = 'training'
                t_membership.value = training
                db.session.add(t_membership)
        db.session.commit()

    def insert(self):
        member = Member()
        member.camp_idx = Camp.get_idx('cmc')
        member.userid = self.userid.data
        member.pwd = self.pwd.data
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
        if self.fullcamp_yn.data == 1:
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = date_list[0][0]
            member.date_of_leave = date_list[-1][0]
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.group_idx = None
        member.regdate = datetime.datetime.today()
        member.canceldate = None
        member.cancel_yn = 0
        member.cancel_reason = None
        member.memo = self.memo.data
        member.room_idx = None
        member.smallgroup_num = None
        db.session.add(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return member.idx

    def update(self, idx):
        member = db.session.query(Member).filter(Member.idx == idx).one()
        db.session.query(Membership).filter(Membership.member_idx == member.idx).delete()
        member.camp_idx = Camp.get_idx('cmc')
        member.userid = self.userid.data
        if self.pwd.data is not None and self.pwd.data != '':
            member.pwd = self.pwd.data
        member.name = self.name.data
        member.area_idx = self.area_idx.data
        member.contact = request.form.get('hp') + '-' + request.form.get('hp2') + '-' + request.form.get('hp3')
        member.church = self.church.data
        member.birth = self.birth.data
        member.sex = self.sex.data
        member.bus_yn = self.bus_yn.data
        member.mit_yn = self.mit_yn.data
        member.newcomer_yn = self.newcomer_yn.data
        member.persontype = self.persontype.data
        member.fullcamp_yn = self.fullcamp_yn.data
        if self.fullcamp_yn.data == 1:
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = date_list[0][0]
            member.date_of_leave = date_list[-1][0]
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.memo = self.memo.data
        db.session.commit()
        self.populate_membership(member.idx)
        return
