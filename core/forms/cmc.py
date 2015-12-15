# -*-coding:utf-8-*-
from wtforms import Form, StringField, SelectField, RadioField, PasswordField
from wtforms.widgets import TextArea
from core.models import Area, Camp
from core.forms import ContactField, MultiCheckboxField


class RegistrationForm(Form):
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
    job = SelectField(
        u'직업/직종',
        choices=[
            (u'정치행정', u'정치행정'), (u'법률', u'법률'), (u'보건의료', u'보건의료'), (u'종교', u'종교'), (u'사회복지', u'사회복지'),
            (u'문화예술스포츠', u'문화예술스포츠'), (u'정치행정', u'정치행정'), (u'경제금융', u'경제금융'), (u'연구기술', u'연구기술'), (u'교육', u'교육'),
            (u'사무관리', u'사무관리'), (u'판매서비스', u'판매서비스'), (u'기곅능', u'기계기능'), (u'취업준비', u'취업준비'), (u'군인', u'군인'), (u'기타', u'기타'),
        ]
    )
    campus = StringField(u'캠퍼스')
    major = StringField(u'전공')
    bus_yn = RadioField(u'단체버스 이용', choices=[(1, u'예'), (0, u'아니오')])
    mit_yn = RadioField(u'FO/MIT 참가', choices=[(1, u'예'), (0, u'아니오')])
    fullcamp_yn = RadioField(u'참가형태', choices=[(1, u'전체참가'), (0, u'부분참가')])
    date_of_arrival = SelectField(u'캠프오는날', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    date_of_leave = SelectField(u'집에가는', choices=Camp.get_date_list(Camp.get_idx('cmc')))
    sm_yn = RadioField(u'SM(학생선교사) 여부', choices=[(1, u'예'), (0, u'아니오')])
    newcomer_yn = RadioField(u'선교캠프가<br/>처음인가요?', choices=[(1, u'예'), (0, u'아니오')])
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
