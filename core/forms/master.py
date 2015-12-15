# -*-coding:utf-8-*-
from wtforms import Form, StringField, HiddenField


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
