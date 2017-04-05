''' 하나의 폼 양식을 여러 곳에서 재활용하기 위해 선언된 wtforms 클래스를 모아둔 모듈'''
import datetime
import hashlib
from flask import request
from wtforms import Form, StringField, SelectField, SelectMultipleField, PasswordField, HiddenField, RadioField
from wtforms.widgets import TextArea, ListWidget, CheckboxInput, HiddenInput
from core.models import Area, Group, Camp, Member, Membership
from core.database import DB as db
from core import form_config


class ContactField(StringField):
    ''' 연락처 필드'''
    data = ""


class MultiCheckboxField(SelectMultipleField):
    ''' 다중 선택을 위한 필드'''
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    data = ""


class RoomCheckForm(Form):
    ''' 숙소 배치 확인을 위한 폼'''
    contact = ContactField('연락처')
    name = StringField('이름')
    logintype = RadioField('구분', choices=[('개인', '개인'), ('단체', '단체')])

    def set_form_data(self, contact, name, logintype):
        ''' 폼의 내용을 입력함'''
        self.contact.data = contact
        self.name.data = name
        self.logintype.data = logintype


class AreaForm(Form):
    ''' 크로스에서 지부 설정 변경을 위한 폼'''
    idx = HiddenField()
    name = StringField('지부명')
    type = SelectField('유형', choices=[("1", '1: 국내'), ("2", '2: 해외'), ("3", '3: 기타'), ("4", '4: 오류')])
    camp = StringField('캠프')

    def set_area_data(self, area):
        ''' area 모델의 내용을 폼에 적용함'''
        self.idx.data = area.idx
        self.name.data = area.name
        self.type.data = area.type
        self.camp.data = area.camp


class GroupForm(Form):
    ''' 단체 등록 및 수정을 위한 폼'''
    camp = ''
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
        ''' 어떤 캠프의 단체등록 폼인지 지정함'''
        self.camp = camp
        self.area_idx.choices = Area.get_list(camp)
        if camp == 'youth':
            self.grouptype.choices = form_config.GROUP_TYPES[camp]
        else:
            self.grouptype.widget = HiddenInput()

        if camp == 'ws':
            self.leaderjob.widget = HiddenInput()

    def set_group_data(self, group):
        ''' group 모델의 내용을 폼에 적용함'''
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
        ''' 폼의 내용을 group 모델 오브젝트에 저장함'''
        group.name = self.name.data
        group.leadername = self.leadername.data
        hp1 = request.form.get('hp')
        hp2 = request.form.get('hp2')
        hp3 = request.form.get('hp3')
        contact = "{0}-{1}-{2}".format(hp1, hp2, hp3)
        group.leadercontact = contact
        group.leaderjob = self.leaderjob.data
        group.area_idx = self.area_idx.data
        group.memo = self.memo.data

    def insert(self, camp_idx):
        ''' 폼으로 입력받은 정보를 바탕으로 새로운 group 정보를 데이터베이스에 저장'''
        group = Group()
        group.camp_idx = camp_idx
        group.regdate = datetime.datetime.today()
        group.groupid = request.form.get('groupid')
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
        ''' 폼으로 입력받은 정보를 바탕으로 기존 group 정보를 데이터베이스에 업데이트'''
        group = db.session.query(Group).filter(Group.idx == idx).one()
        if self.pwd.data is not None and self.pwd.data != '':
            group.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        self.populate_obj(group)
        db.session.commit()

# 생년월일 선택을 위한 년도 리스트.
YEARS = [("{0}".format(i), "{0}".format(i)) for i in range(2015, 1920, -1)]


class RegistrationForm(Form):
    ''' 캠프 신청을 위한 폼. 개인 또는 단체의 멤버s'''
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

    # added by Moon 2017.4.5
    military = StringField('계급/소속부대')

    stafftype = RadioField('스탭구분')  # membership for ws
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
    # membership for ['cmc', 'cbtj']
    vision_yn = RadioField('비전스쿨 수료여부', choices=[('1', '예'), ('0', '아니오')])
    training = MultiCheckboxField('인터콥 훈련여부')  # membership for all
    route = MultiCheckboxField('선교캠프를<br/>알게된 경로')  # membership for ['youth']
    language = SelectField('통역필요', choices=[(i, i) for i in form_config.LANGUAGES])
    memo = StringField('남기고싶은 말', widget=TextArea())

    enname = StringField('영문이름')
    address = StringField('교회주소')
    denomination = StringField('교단')
    location = SelectField('지역', choices=[('국내', '국내'), ('해외', '해외')])
    city = StringField('도시')
    etclanguage = StringField('기타통역언어')
    etcperson = SelectField('세부구분', choices=[
        ('', '선택하세요'),
        ('여성시니어', '여성시니어'),
        ('스텝', '스텝'),
        ('청년', '청년'),
        ('청소년', '청소년'),
        ('어린이', '어린이'),
        ('키즈', '키즈')
    ])



    def set_camp(self, camp):
        ''' 어떤 캠프의 신청폼인지 지정해줌.
        '''
        self.camp = camp
        self.date_of_arrival.choices = Camp.get_date_list(Camp.get_idx(camp))
        self.date_of_leave.choices = Camp.get_date_list(Camp.get_idx(camp))

        if camp != 'ga':
            self.address.widget = HiddenInput()
            self.location.widget = HiddenInput()
            self.city.widget = HiddenInput()
            self.etclanguage.widget = HiddenInput()
            self.enname.widget = HiddenInput()
            self.etcperson.widget = HiddenInput()
            self.denomination.widget = HiddenInput()

            self.area_idx.choices = Area.get_list(camp)
            self.persontype.choices = [(i, i) for i in form_config.PERSONTYPES[camp]]
            self.training.choices = form_config.TRAININGS[camp]
            if camp != 'cbtj':
                self.job_name.widget = HiddenInput()

            if camp != 'cmc':
                self.campus.widget = HiddenInput()
                self.major.widget = HiddenInput()
            
            # added by Moon 2017.4.5
            if camp not in ['cmc', 'cbtj'] or self.job_name != '군인':    
                self.military.widget =HiddenInput()
            #

            if camp in ['cmc', 'cbtj']:
                self.job.choices = [(i, i) for i in form_config.JOBS]
            else:
                self.vision_yn.widget = HiddenInput()
                self.mit_yn.widget = HiddenInput()
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

            if camp == 'kids':
                self.bus_yn.widget = HiddenInput()
                self.language.widget = HiddenInput()
                self.fullcamp_yn.widget = HiddenInput()
                self.date_of_arrival.widget = HiddenInput()
                self.date_of_leave.widget = HiddenInput()

            if camp == 'youth':
                self.route.choices = form_config.ROUTES[camp]
            else:
                self.route.widget = HiddenInput()
        else:  # camp == 'ga'
            self.userid.widget = HiddenInput()
            self.area_idx.widget = HiddenInput()
            self.pwd.widget = HiddenInput()
            self.pwd2.widget = HiddenInput()
            self.birth.widget = HiddenInput()
            self.stafftype.widget = HiddenInput()
            self.job.widget = HiddenInput()
            self.job_name.widget = HiddenInput()
            self.campus.widget = HiddenInput()
            self.major.widget = HiddenInput()
            self.sch1.widget = HiddenInput()
            self.sch2.widget = HiddenInput()
            self.bus_yn.widget = HiddenInput()
            self.newcomer_yn.widget = HiddenInput()
            self.vision_yn.widget = HiddenInput()
            self.training.widget = HiddenInput()
            self.route.label = 'GA를 알게된 경로'
            self.route.choices = [
                ('주변사람들의 추천', "주변사람들의 추천"), ('언론매체 및 홍보물', "언론매체 및 홍보물"),
                ('인터콥소속 선교사 파송교회', "인터콥소속 선교사 파송교회"), ('인터콥 협력교회', "인터콥 협력교회"),
                ('목선협', "목선협"), ('목회자 비전스쿨', "목회자 비전스쿨"),
                ('기타', "기타"),
            ]
            self.mit_yn.label = "비전캠프 참석 여부"
            self.persontype.choices = [('목회자', '목회자'), ('비목회자', '비목회자')]
            self.language.choices = [('필요 없음', '필요 없음'), ('영어', '영어'), ('중국어', '중국어'), ('그 외 언어', '그 외 언어')]


    def set_group_mode(self, group_idx, group_area_idx):
        ''' 개인 신청인지 단체의 멤버신청인지 정해줌'''
        self.group_yn = True
        self.userid.widget = HiddenInput()
        self.pwd.widget = HiddenInput()
        self.pwd2.widget = HiddenInput()
        self.area_idx.widget = HiddenInput()
        self.group_idx = group_idx
        self.group_area_idx = group_area_idx
        self.sch1.widget = HiddenInput()
        self.sch2.widget = HiddenInput()

    def set_member_data(self, member):
        ''' member 모델 객체의 내용으로 폼을 채움'''
        membership_data = member.get_membership_data()
        self.idx.data = member.idx
        if member.group_idx is None:
            self.userid.data = member.userid
        self.area_idx.data = member.area_idx
        self.name.data = member.name
        self.sex.data = member.sex
        if self.camp != 'ga':
            self.birth.data = member.birth[:4]
        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        # added by Moon 2017.4.5
        if self.camp == 'cmc' or self.camp == 'cbtj':
            self.military.data = member.military

        if self.camp != 'ga':
            self.bus_yn.data = member.bus_yn
        self.mit_yn.data = member.mit_yn
        self.fullcamp_yn.data = member.fullcamp_yn
        self.date_of_arrival.data = member.date_of_arrival
        self.date_of_leave.data = member.date_of_leave
        if self.camp != 'ga':
            self.newcomer_yn.data = member.newcomer_yn
            self.training.data = membership_data.get('training')
        self.language.data = member.language
        self.memo.data = member.memo

        # set membership data
        for membership_field in form_config.MEMBERSHIP_FIELDS[self.camp]:
            getattr(self, membership_field).data = membership_data.get(membership_field)

    def populate_obj(self, member):
        ''' 폼의 내용으로 member 모델 객체의 내용을 채움'''
        member.name = self.name.data
        if self.camp != 'ga':
            if self.group_yn is False:
                member.area_idx = self.area_idx.data
            else:
                member.area_idx = self.group_area_idx
        member.contact = request.form.get('hp') + '-' + request.form.get('hp2') + '-' + request.form.get('hp3')
        member.church = self.church.data
        if self.camp != 'ga':
            member.birth = self.birth.data
        member.sex = self.sex.data
        if self.camp != 'ga':
            member.bus_yn = self.bus_yn.data if self.bus_yn not in [None, 'None', '', 'none', 'null'] else 0
        member.mit_yn = self.mit_yn.data if self.mit_yn not in [None, 'None', '', 'none', 'null'] else 0
        member.attend_yn = 0
        if self.camp != 'ga':
            member.newcomer_yn = self.newcomer_yn.data
        member.persontype = self.persontype.data
        # added by Moon 2017.4.5
        if self.camp == 'cmc' or self.camp == 'cbtj':
            member.military = self.military.data

        member.fullcamp_yn = self.fullcamp_yn.data if self.fullcamp_yn not in [None, 'None', '', 'none', 'null'] else 1
        if self.camp == 'kids' or self.fullcamp_yn.data == "1":
            date_list = Camp.get_date_list(member.camp_idx)
            member.date_of_arrival = datetime.datetime.strftime(date_list[0][0], "%Y-%m-%d")
            member.date_of_leave = datetime.datetime.strftime(date_list[-1][0], "%Y-%m-%d")
        else:
            member.date_of_arrival = self.date_of_arrival.data
            member.date_of_leave = self.date_of_leave.data
        member.language = self.language.data
        member.memo = self.memo.data

    def populate_membership(self, member_idx):
        ''' member의 가변필드인 membership 테이블에 폼의 내용을 업데이트함.
        '''
        camp_idx = Camp.get_idx(self.camp)
        membership_fields = form_config.MEMBERSHIP_FIELDS[self.camp]

        for membership_field in membership_fields:
            if membership_field == 'route':
                for route in getattr(self, membership_field).data:
                    r_membership = Membership()
                    r_membership.camp_idx = camp_idx
                    r_membership.member_idx = member_idx
                    r_membership.key = 'route'
                    r_membership.value = route
                    db.session.add(r_membership)
            else:
                if getattr(self, membership_field).data not in [None, '', 'none']:
                    membership = Membership()
                    membership.camp_idx = camp_idx
                    membership.member_idx = member_idx
                    membership.key = membership_field
                    membership.value = getattr(self, membership_field).data
                    db.session.add(membership)

        if self.camp != 'ga':
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
        ''' 폼의 내용을 가지고 member테이블에 신규 행을 삽입함.
        '''
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

        attend = member.get_attend_array()
        member.attend1, member.attend2, member.attend3, member.attend4 = attend
        db.session.add(member)
        db.session.commit()
        self.populate_membership(member.idx)
        return member.idx

    def update(self, idx):
        ''' 폼의 내용을 가지고 member테이블의 기존 행을 업데이트함.
        '''
        member = db.session.query(Member).filter(Member.idx == idx).one()
        db.session.query(Membership).filter(Membership.member_idx == member.idx).delete()
        if self.pwd.data is not None and self.pwd.data != '':
            member.pwd = hashlib.sha224(self.pwd.data.encode('utf-8')).hexdigest()
        self.populate_obj(member)
        attend = member.get_attend_array()
        member.attend1, member.attend2, member.attend3, member.attend4 = attend
        db.session.commit()
        self.populate_membership(member.idx)
        return
