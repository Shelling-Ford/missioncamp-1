# -*-coding:utf-8-*-
from flask import request
from wtforms import Form, StringField, SelectField, SelectMultipleField, PasswordField, HiddenField, RadioField
from wtforms.widgets import TextArea, ListWidget, CheckboxInput
from core.models import Area, Group
from core.database import db
import datetime
import hashlib


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
    grouptype = HiddenField()
    leadername = StringField(u'담당자 이름')
    leadercontact = ContactField(u'담당자 연락처')
    leaderjob = StringField(u'담당자 직업')
    area_idx = SelectField(u'등록지부', choices=Area.get_list('*'))
    memo = StringField(u'남기고싶은 말', widget=TextArea())
    group_idx = HiddenField()

    def set_camp(self, camp):
        self.area_idx = SelectField(u'등록지부', choices=Area.get_list(camp))
        if camp == 'youth':
            self.grouptype = RadioField(u'단체 유형', choices=[('1', '다니엘과 세친구'), ('2', '예수님과 열두제자'), ('3', '단체교회')])

    def set_group_data(self, group):
        self.groupid.data = group.groupid
        self.name.data = group.name
        self.leadername.data = group.leadername
        self.leadercontact.data = group.leadercontact
        self.leaderjob.data = group.leaderjob
        self.area_idx.data = group.area_idx
        self.memo.data = group.memo
        self.group_idx.data = group.idx

    def populate_obj(self, group):
        group.groupid = self.groupid.data
        group.name = self.name.data
        group.leadername = self.leadername.data
        group.leadercontact = request.form.get('hp') + '-' + request.form.get('hp2') + '-' + request.form.get('hp3')
        group.leaderjob = self.leaderjob.data
        group.area_idx = self.area_idx.data
        group.memo = self.memo.data

    def insert(self, camp_idx):
        group = Group()
        group.camp_idx = camp_idx
        group.regdate = datetime.datetime.today()
        group.pwd = hashlib.sha224(self.pwd.data).hexdigest()
        self.populate_obj(group)
        group.cancel_yn = 0
        group.cancel_reason = None
        group.cancedate = None
        group.mem_num = 0
        db.session.add(group)
        db.session.commit()
        return group.idx

    def update(self, camp_idx, idx):
        group = Group.get(idx)
        if self.pwd.data is not None and self.pwd.data != '':
            group.pwd = hashlib.sha224(self.pwd.data).hexdigest()
        self.populate_obj(group)
        db.session.commit()


class RoomCheckForm(Form):
    contact = ContactField(u'연락처')
    name = StringField(u'이름')
    logintype = RadioField(u'구분', choices=[(u'개인', u'개인'), (u'단체', u'단체')])
