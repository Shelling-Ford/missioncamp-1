# -*-coding:utf-8-*-
from wtforms import Form, StringField, SelectField, SelectMultipleField, PasswordField, HiddenField, RadioField
from wtforms.widgets import TextArea, ListWidget, CheckboxInput
from core.models import Area


class ContactField(StringField):
    pass


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class GroupForm(Form):
    groupid = StringField(u'단체 아이디')
    pwd = PasswordField(u'비밀번호')
    pwd2 = PasswordField(u'비밀번호 확인')
    name = StringField(u'단체이름')
    # grouptype = RadioField(u'단체 유형', choices=[('1', '다니엘과 세친구'), ('2', '예수님과 열두제자'), ('3', '단체교회')])
    leadername = StringField(u'담당자 이름')
    leadercontact = ContactField(u'담당자 연락처')
    leaderjob = StringField(u'담당자 직업')
    area_idx = SelectField(u'등록지부', choices=Area.get_list('kids'))
    memo = StringField(u'남기고싶은 말', widget=TextArea())
    group_idx = HiddenField()

    def set_group_data(self, group):
        self.groupid.data = group.groupid
        self.name.data = group.name
        self.leadername.data = group.leadername
        self.leadercontact.data = group.leadercontact
        self.leaderjob.data = group.leaderjob
        self.area_idx.data = group.area_idx
        self.memo.data = group.memo
        self.group_idx.data = group.idx


class RoomCheckForm(Form):
    contact = ContactField(u'연락처')
    name = StringField(u'이름')
    logintype = RadioField(u'구분', choices=[(u'개인', u'개인'), (u'단체', u'단체')])
