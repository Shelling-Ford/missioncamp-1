import datetime
import hashlib
from flask import request
from wtforms import Form, StringField, SelectField, SelectMultipleField, PasswordField, HiddenField, RadioField
from wtforms.widgets import TextArea, ListWidget, CheckboxInput, HiddenInput
from core.models import Area, Group, Camp, Member, Membership
from core.database import db
from core import form_config


class ContactField(StringField):
    pass


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RoomCheckForm(Form):
    contact = ContactField('연락처')
    name = StringField('이름')
    logintype = RadioField('구분', choices=[('개인', '개인'), ('단체', '단체')])


class AreaForm(Form):
    idx = HiddenField()
    name = StringField(u'지부명')
    type = StringField(u'유형')
    camp = StringField(u'캠프')

    def set_area_data(self, area):
        self.idx.data = area.idx
        self.name.data = area.name
        self.type.data = area.type
        self.camp.data = area.camp


class GroupForm(Form):
    groupid = StringField('단체 아이디')
    pwd = PasswordField('비밀번호')
    pwd2 = PasswordField('비밀번호 확인')
    name = StringField('단체이름')
    grouptype = RadioField('단체 유형')
    leadername = StringField('담당자 이름')
    leadercontact = ContactField('담당자 연락처')
    leaderjob = StringField('담당자 직업')
    area_idx = SelectField('등록지부', choices=Area.get_list('*'))
    memo = StringField('남기고싶은 말', widget=TextArea())
    group_idx = HiddenField()

    def set_camp(self, camp):
        self.area_idx.choices = Area.get_list(camp)
        if camp == 'youth':
            self.grouptype.choices = form_config.GROUP_TYPES[camp]
        else:
            self.grouptype.widget = HiddenInput()

    def set_group_data(self, group):
        self.groupid.data = group.groupid
        self.name.data = group.name
        self.leadername.data = group.leadername
        self.leadercontact.data = group.leadercontact
        self.leaderjob.data = group.leaderjob
        self.area_idx.data = group.area_idx
        self.memo.data = group.memo
        self.group_idx.data = group.idx

        if self.camp == 'youth':
            self.grouptype.data = group.grouptype

    def populate_obj(self, group):
        group.groupid = self.groupid.data
        group.name = self.name.data
        group.leadername = self.leadername.data
        hp = request.form.get('hp')
        hp2 = request.form.get('hp2')
        hp3 = request.form.get('hp3')
        contact = "{0}-{1}-{2}".format(hp, hp2, hp3)
        group.leadercontact = contact
        group.leaderjob = self.leaderjob.data
        group.area_idx = self.area_idx.data
        group.memo = self.memo.data

    def insert(self, camp_idx):
        group = Group()
        group.camp_idx = camp_idx
        group.regdate = datetime.datetime.today()
        group.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        self.populate_obj(group)
        group.cancel_yn = 0
        group.cancel_reason = None
        group.cancedate = None
        group.mem_num = 0
        db.session.add(group)
        db.session.commit()
        return group.idx

    def update(self, idx):
        group = Group.get(idx)
        if self.pwd.data is not None and self.pwd.data != '':
            group.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        self.populate_obj(group)
        db.session.commit()


YEARS = [("{0}".format(i), "{0}".format(i)) for i in range(2015, 1940, -1)]


class RegistrationForm(Form):
    group_yn = False
    camp = ''
    group_idx = None
    group_area_idx = None
    idx = HiddenField()
    group_idx = HiddenField()
    userid = StringField('아이디(이메일)')
    pwd = PasswordField('비밀번호')
    pwd2 = PasswordField('비밀번호 확인')
    name = StringField('이름')
    pname = StringField('보호자 성함')  # membership for ws
    area_idx = SelectField('지부', choices=Area.get_list('*'))
    sex = RadioField('성별', choices=[('M', '남'), ('F', '여')])
    birth = SelectField('출생년도', choices=YEARS)
    contact = ContactField('연락처')
    church = StringField('소속교회')
    persontype = RadioField('참가구분')
    stafftype = RadioField('스탭구분') # membership for ws
    job = SelectField('직업/직종')  # membership for ['cmc', 'cbtj']
    job_name = StringField('직장명')  # membership for cbtj
    campus = StringField('캠퍼스')  # membership for cmc
    major = StringField('전공')  # membership for cmc
    sch1 = StringField('학교')  # membership for kids
    sch2 = SelectField('학년')  # membership for kids
    bus_yn = RadioField('단체버스 이용', choices=[(1, '예'), (0, '아니오')])
    mit_yn = RadioField('2017 겨울 FO/MIT 참가', choices=[(1, '예'), (0, '아니오')])
    fullcamp_yn = RadioField('참가형태', choices=[(1, '전체참가'), (0, '부분참가')])
    date_of_arrival = SelectField('캠프오는날')
    date_of_leave = SelectField('집에가는날')
    newcomer_yn = RadioField('선교캠프가<br/>처음인가요?', choices=[(1, '예'), (0, '아니오')])
    vision_yn = RadioField('비전스쿨 수료여부', choices=[(1, '예'), (0, '아니오')])  # membership for ['cmc', 'cbtj']
    training = MultiCheckboxField('인터콥 훈련여부')  # membership for all
    language = SelectField('통역필요', choices=[(i, i) for i in form_config.LANGUAGES])
    memo = StringField('남기고싶은 말', widget=TextArea())

    def set_camp(self, camp):
        self.camp = camp
        self.area_idx.choices = Area.get_list(camp)
        self.persontype.choices = [(i, i) for i in form_config.PERSONTYPES[camp]]
        self.date_of_arrival.choices = Camp.get_date_list(Camp.get_idx(camp))
        self.date_of_leave.choices = Camp.get_date_list(Camp.get_idx(camp))
        self.training.choices = form_config.TRAININGS[camp]

        if camp != 'cbtj':
            self.job_name.widget = HiddenInput()

        if camp != 'cmc':
            self.campus.widget = HiddenInput()
            self.major.widget = HiddenInput()

        if camp in ['cmc', 'cbtj']:
            self.job.choices = [(i, i) for i in form_config.JOBS]
        else:
            self.vision_yn.widget = HiddenInput()

        if camp not in ['ws', 'kids']:
            self.pname.widget = HiddenInput()
        else:
            self.userid.label = '아이디'

        if camp != 'ws':
            self.stafftype.widget = HiddenInput()
        else:
            self.job.label = '교회 직분'
            self.job.choices = [(i, i) for i in form_config.CHURCH_JOBS]
            self.stafftype.choices = form_config.STAFF_TYPES[camp]

        if camp not in ['cbtj', 'cmc', 'ws']:
            self.job.widget = HiddenInput()

        if camp not in ['kids', 'youth']:
            self.sch1.widget = HiddenInput()
            self.sch2.widget = HiddenInput()
        else:
            self.sch2.choices = form_config.SCH2_CHOICES[camp]
            self.mit_yn.widget = HiddenInput()

        if camp == 'kids':
            self.bus_yn.widget = HiddenInput()
            self.language.widget = HiddenInput()
            self.fullcamp_yn.widget = HiddenInput()
            self.date_of_arrival.widget = HiddenInput()
            self.date_of_leave.widget = HiddenInput()


    def set_group_mode(self, group_idx, group_area_idx):
        self.group_yn = True
        self.userid.widget = HiddenInput()
        self.pwd.widget = HiddenInput()
        self.pwd2.widget = HiddenInput()
        self.area_idx.widget = HiddenInput()
        print(self.area_idx.widget.__class__.__name__)
        self.group_idx = group_idx
        self.group_area_idx = group_area_idx
        self.sch1.widget = HiddenInput()
        self.sch2.widget = HiddenInput()

    def set_member_data(self, member):
        membership_data = member.get_membership_data()
        self.idx.data = member.idx
        if member.group_idx is None:
            self.userid.data = member.userid
            self.area_idx.data = member.area_idx
        self.name.data = member.name
        self.sex.data = member.sex
        self.birth.data = member.birth[:4]
        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        self.bus_yn.data = member.bus_yn
        self.mit_yn.data = member.mit_yn
        self.fullcamp_yn.data = member.fullcamp_yn
        self.date_of_arrival.data = member.date_of_arrival
        self.date_of_leave.data = member.date_of_leave
        self.newcomer_yn.data = member.newcomer_yn
        self.training.data = membership_data.get('training')
        self.language.data = member.language
        self.memo.data = member.memo

        # set membership data
        for membership_field in form_config.MEMBERSHIP_FIELDS[self.camp]:
            getattr(self, membership_field).data = membership_data.get(membership_field)

    def populate_obj(self, member):
        member.name = self.name.data
        if self.group_yn is False:
            member.area_idx = self.area_idx.data
        else:
            member.area_idx = self.group_area_idx
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
        if self.fullcamp_yn.data == "1":
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = datetime.datetime.strftime(date_list[0][0], "%Y-%m-%d")
            member.date_of_leave = datetime.datetime.strftime(date_list[-1][0], "%Y-%m-%d")
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.memo = self.memo.data

    def populate_membership(self, member_idx):
        camp_idx = Camp.get_idx(self.camp)
        membership_fields = form_config.MEMBERSHIP_FIELDS[self.camp]

        for membership_field in membership_fields:
            if getattr(self, membership_field).data not in [None, '', 'none']:
                membership = Membership()
                membership.camp_idx = camp_idx
                membership.member_idx = member_idx
                membership.key = membership_field
                membership.value = getattr(self, membership_field).data
                db.session.add(membership)

        if self.training.data not in [None, '', 'None']:
            for training in self.training.data:
                t_membership = Membership()
                t_membership.camp_idx = camp_idx
                t_membership.member_idx = member_idx
                t_membership.key = 'training'
                t_membership.value = training
                db.session.add(t_membership)
        db.session.commit()

    def insert(self):
        member = Member()
        member.camp_idx = Camp.get_idx(self.camp)
        if self.group_yn is False:
            member.userid = self.userid.data
            member.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        else:
            member.group_idx = self.group_idx
        self.populate_obj(member)
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
            member.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        self.populate_obj(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return
