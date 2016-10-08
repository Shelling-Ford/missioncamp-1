# -*-coding:utf-8-*-
from wtforms import Form, StringField, SelectField, RadioField, PasswordField, HiddenField
from wtforms.widgets import TextArea
from core.models import Area
from core.forms import ContactField, MultiCheckboxField


sch2_choices = [(u'예비1학년', u'예비1학년')]
sch2_choices.extend([(unicode(i), unicode(i)+unicode('학년')) for i in range(1, 7)])


class RegistrationForm(Form):
    userid = StringField(u'아이디')
    pwd = PasswordField(u'비밀번호')
    pwd2 = PasswordField(u'비밀번호 확인')
    name = StringField(u'이름')
    area_idx = SelectField(u'지부', choices=Area.get_list('kids'))
    sex = RadioField(u'성별', choices=[('M', u'남'), ('F', u'여')])
    birth = SelectField(u'출생년도', choices=[(unicode(i), unicode(i)) for i in range(2015, 1940, -1)])
    pname = StringField(u'보호자이름')
    contact = ContactField(u'보호자연락처')
    church = StringField(u'소속교회')
    persontype = RadioField(
        u'참가구분',
        choices=[
            (u'어린이', u'어린이'), (u'교사', u'교사'), (u'교역자', u'교역자'), (u'예배팀', u'예배팀'), (u'키즈스탭', u'키즈스탭'), (u'유스탭', u'유스탭'),
            (u'선캠팀장', u'선캠팀장'), (u'중보스탭', u'중보스탭'), (u'캠프스탭', u'캠프스탭'), (u'기쁜맘', u'기쁜맘'), (u'선교사', u'선교사'), (u'MIT', u'MIT'), (u'MIT교사', u'MIT교사'), (u'기타', u'기타')
        ]
    )
    sch1 = StringField(u'학교')
    sch2 = SelectField(u'학년', choices=sch2_choices)
    newcomer_yn = RadioField(u'선교캠프가<br/>처음인가요?', choices=[(1, u'예'), (0, u'아니오')])
    training = MultiCheckboxField(
        u'인터콥 훈련여부',
        choices=[
            ('training1', u'어린이비전스쿨'), ('training2', u'월드미션'), ('training3', u'선교캠프'), ('training4', u'MIT'), ('none', u'없음')
        ]
    )
    memo = StringField(u'남기고싶은 말', widget=TextArea())

    def set_member_data(self, member):
        membership = member.get_membership_data()
        self.userid.data = member.userid
        self.name.data = member.name
        self.area_idx.data = member.area_idx
        self.sex.data = member.sex
        self.birth.data = member.birth
        self.training.data = membership.get('training', [])
        self.pname.data = membership.get('pname')
        self.sch1.data = membership.get('sch1')
        self.sch2.data = membership.get('sch2')
        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        self.newcomer_yn.data = member.newcomer_yn
        self.memo.data = member.memo


class GroupMemberRegForm(Form):
    group_idx = HiddenField()
    name = StringField(u'이름')
    area_idx = HiddenField()
    sex = RadioField(u'성별', choices=[('M', u'남'), ('F', u'여')])
    birth = SelectField(u'출생년도', choices=[(unicode(i), unicode(i)) for i in range(2015, 1940, -1)])
    pname = StringField(u'보호자이름')
    contact = ContactField(u'보호자연락처')
    persontype = RadioField(
        u'참가구분',
        choices=[
            (u'어린이', u'어린이'), (u'교사', u'교사'), (u'교역자', u'교역자'), (u'예배팀', u'예배팀'), (u'키즈스탭', u'키즈스탭'), (u'유스탭', u'유스탭'),
            (u'선캠팀장', u'선캠팀장'), (u'중보스탭', u'중보스탭'), (u'캠프스탭', u'캠프스탭'), (u'기쁜맘', u'기쁜맘'), (u'선교사', u'선교사'), (u'MIT', u'MIT'), (u'MIT교사', u'MIT교사'), (u'기타', u'기타')
        ]
    )
    newcomer_yn = RadioField(u'선교캠프가<br/>처음인가요?', choices=[(1, u'예'), (0, u'아니오')])
    training = MultiCheckboxField(
        u'인터콥 훈련여부',
        choices=[
            ('training1', u'어린이비전스쿨'), ('training2', u'월드미션'), ('training3', u'선교캠프'), ('training4', u'MIT'), ('none', u'없음')
        ]
    )

    def set_group_idx(self, group_idx):
        self.group_idx.data = int(group_idx)

    def set_area_idx(self, area_idx):
        self.area_idx.data = int(area_idx)

    def set_member_data(self, member):
        membership = member.get_membership_data()
        self.group_idx.data = member.group_idx
        self.name.data = member.name
        self.sex.data = member.sex
        self.birth.data = member.birth
        self.training.data = membership.get('training', [])
        self.pname.data = membership.get('pname')
        self.contact.data = member.contact
        self.persontype.data = member.persontype
        self.newcomer_yn.data = member.newcomer_yn
