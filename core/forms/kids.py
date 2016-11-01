# -*-coding:utf-8-*-
from wtforms import Form, StringField, SelectField, RadioField, PasswordField, HiddenField
from wtforms.widgets import TextArea
from core.models import Area
from core.forms import ContactField, MultiCheckboxField


sch2_choices = [('예비1학년', '예비1학년')]
sch2_choices.extend([("{0}".format(i), "{0} 학년".format(i)) for i in range(1, 7)])


class RegistrationForm(Form):
    userid = StringField('아이디')
    pwd = PasswordField('비밀번호')
    pwd2 = PasswordField('비밀번호 확인')
    name = StringField('이름')
    area_idx = SelectField('지부', choices=Area.get_list('kids'))
    sex = RadioField('성별', choices=[('M', '남'), ('F', '여')])
    birth = SelectField('출생년도', choices=[("{0}".format(i), "{0}".format(i)) for i in range(2015, 1940, -1)])
    pname = StringField('보호자이름')
    contact = ContactField('보호자연락처')
    church = StringField('소속교회')
    persontype = RadioField(
        '참가구분',
        choices=[
            ('어린이', '어린이'), ('교사', '교사'), ('교역자', '교역자'), ('예배팀', '예배팀'), ('키즈스탭', '키즈스탭'), ('유스탭', '유스탭'),
            ('선캠팀장', '선캠팀장'), ('중보스탭', '중보스탭'), ('캠프스탭', '캠프스탭'), ('기쁜맘', '기쁜맘'), ('선교사', '선교사'), ('MIT', 'MIT'), ('MIT교사', 'MIT교사'), ('기타', '기타')
        ]
    )
    sch1 = StringField('학교')
    sch2 = SelectField('학년', choices=sch2_choices)
    newcomer_yn = RadioField('선교캠프가<br/>처음인가요?', choices=[(1, '예'), (0, '아니오')])
    training = MultiCheckboxField(
        '인터콥 훈련여부',
        choices=[
            ('training1', '어린이비전스쿨'), ('training2', '월드미션'), ('training3', '선교캠프'), ('training4', 'MIT'), ('none', '없음')
        ]
    )
    memo = StringField('남기고싶은 말', widget=TextArea())

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
    name = StringField('이름')
    area_idx = HiddenField()
    sex = RadioField('성별', choices=[('M', '남'), ('F', '여')])
    birth = SelectField('출생년도', choices=[("{0}".format(i), "{0}".format(i)) for i in range(2015, 1940, -1)])
    pname = StringField('보호자이름')
    contact = ContactField('보호자연락처')
    persontype = RadioField(
        '참가구분',
        choices=[
            ('어린이', '어린이'), ('교사', '교사'), ('교역자', '교역자'), ('예배팀', '예배팀'), ('키즈스탭', '키즈스탭'), ('유스탭', '유스탭'),
            ('선캠팀장', '선캠팀장'), ('중보스탭', '중보스탭'), ('캠프스탭', '캠프스탭'), ('기쁜맘', '기쁜맘'), ('선교사', '선교사'), ('MIT', 'MIT'), ('MIT교사', 'MIT교사'), ('기타', '기타')
        ]
    )
    newcomer_yn = RadioField('선교캠프가<br/>처음인가요?', choices=[(1, '예'), (0, '아니오')])
    training = MultiCheckboxField(
        '인터콥 훈련여부',
        choices=[
            ('training1', '어린이비전스쿨'), ('training2', '월드미션'), ('training3', '선교캠프'), ('training4', 'MIT'), ('none', '없음')
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
