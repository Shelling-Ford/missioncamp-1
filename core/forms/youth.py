# -*-coding:utf-8-*-
from wtforms import Form, StringField, SelectField, RadioField, PasswordField
from wtforms.widgets import TextArea
from core.models import Area
from core.forms import ContactField, MultiCheckboxField


class RegistrationForm(Form):
    userid = StringField(u'아이디')
    pwd = PasswordField(u'비밀번호')
    pwd2 = PasswordField(u'비밀번호 확인')
    name = StringField(u'이름')
    area_idx = SelectField(u'지부', choices=Area.get_list('youth'))
    sex = RadioField(u'성별', choices=[('M', u'남자'), ('F', u'여자')])
    birth = SelectField(u'출생년도', choices=[(unicode(i), unicode(i)) for i in range(2015, 1940, -1)])
    contact = ContactField(u'연락처')
    church = StringField(u'소속교회')
    persontype = RadioField(u'참가구분', choices=[(u'중학생', u'중학생'), (u'고등학생', u'고등학생'), (u'교사', u'교사'), (u'교역자', u'교역자'), (u'기타', u'기타')])
    sch1 = StringField(u'학교')
    sch2 = SelectField(u'학년', choices=[(unicode(i), unicode(i)+u'학년') for i in range(1, 7)])
    bus_yn = RadioField(u'단체버스 이용', choices=[(1, u'예'), (0, u'아니오')])
    newcomer_yn = RadioField(u'선교캠프가<br/>처음인가요?', choices=[(1, u'예'), (0, u'아니오')])
    training = MultiCheckboxField(
        u'인터콥 훈련여부',
        choices=[
            ('training1', u'청소년비전스쿨'), ('training2', u'Mission Academy'), ('training3', u'U★BTJ Club School'), ('training4', u'UGLC'),
            ('training5', u'청소년월드미션'), ('training6', u'청소년선교캠프'), ('training7', u'청소년MIT,GUMF'), ('training8', u'U★BTJ 운동가'),
            ('none', u'없음')
        ]
    )
    route = MultiCheckboxField(
        u'선캠 참여 경로',
        choices=[
            ('route1', u'지인추천(친구,선생님)'), ('route2', u'교회추천'), ('route3', u'홍보물(포스터,브로셔)'),
            ('route4', u'인터넷(Facebook,포털사이트,카페 등)'), ('route5', u'월드미션'), ('route6', '유비투어'),
            ('route7', u'U★BTJ')
        ]
    )
    memo = StringField(u'남기고싶은 말', widget=TextArea())

    def set_member_data(self, member):
        self.userid.data = member.userid
        self.name.data = member.name
        self.area_idx.data = member.area_idx
        self.sex.data = member.sex
        self.birth.data = member.birth
        self.training.data = []
        self.route.data = []
        for membership in member.membership:
            if membership.key == 'route':
                self.route.data.append(membership.value)
            elif membership.key == 'sch1':
                self.sch1.data = membership.value
            elif membership.key == 'sch2':
                self.sch2.data = membership.value
            elif membership.key == 'training':
                self.training.data.append(membership.value)

        self.contact.data = member.contact
        self.church.data = member.church
        self.persontype.data = member.persontype
        self.bus_yn.data = member.bus_yn
        self.newcomer_yn.data = member.newcomer_yn
        self.memo.data = member.memo
