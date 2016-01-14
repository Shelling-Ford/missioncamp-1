# -*-coding:utf-8-*-
import xlsxwriter
from core.models import Member, Camp

try:
    import cStringIO as StringIO
except:
    import StringIO


def multi_getattr(obj, attr, default=None):
    attributes = attr.split(".")
    for a in attributes:
        try:
            obj = getattr(obj, a)
            if callable(obj):
                obj = obj()
        except AttributeError:
            return default
    return obj if obj is not None else default


class XlsxBuilder():

    def __init__(self):
        self.output = StringIO.StringIO()
        self.workbook = xlsxwriter.Workbook(self.output)
        self.worksheet = self.workbook.add_worksheet()
        self.date_format = self.workbook.add_format({'num_format': 'yyyy-mm-dd'})

    def get_value(self, obj, label):
        boolean = [u'아니오', u'예', u'??']
        ox = ['X', 'O', '??']
        sex = {'M': u'남', 'F': u'여', '': u'오류(미입력)'}
        complete = [u'미납', u'부분납', u'완납']
        func_map = {
            u'이름': multi_getattr(obj, 'name', ''),
            u'지부': multi_getattr(obj, 'area.name', ''),
            u'참가구분': multi_getattr(obj, 'persontype', ''),
            u'출석': ox[multi_getattr(obj, 'attend_yn', 0)],
            u'단체': multi_getattr(obj, 'group.name', ''),
            u'성별': sex[multi_getattr(obj, 'sex', '')],
            u'연락처': multi_getattr(obj, 'contact', ''),
            u'입금상태': complete[multi_getattr(obj, 'payment.complete', 0)],
            u'입금액': multi_getattr(obj, 'payment.amount', ''),
            u'재정클레임': multi_getattr(obj, 'payment.claim', ''),
            u'출석교회': multi_getattr(obj, 'church', ''),
            u'생년월일': multi_getattr(obj, 'birth', ''),
            u'단체버스': boolean[multi_getattr(obj, 'bus_yn', 0)],
            u'MIT': boolean[multi_getattr(obj, 'mit_yn', 0)],
            u'뉴커머': boolean[multi_getattr(obj, 'newcomer_yn', 0)],
            u'전체참석': boolean[multi_getattr(obj, 'fullcamp_yn', 0)],
            u'오는날': multi_getattr(obj, 'date_of_arrival', 0),
            u'가는날': multi_getattr(obj, 'date_of_leave', 0),
            u'통역필요': multi_getattr(obj, 'language', ''),
            u'등록날자': multi_getattr(obj, 'regdate', 0),
            u'숙소': ''.join([multi_getattr(obj, 'room.building', ''), multi_getattr(obj, 'room.number', '')]),
            u'메모': multi_getattr(obj, 'memo', ''),
        }

        return func_map[label]

    def get_membership_value(self, obj, label):
        func_map = {
            u'직업': obj.get('job', ''),
            u'캠퍼스': obj.get('campus', ''),
            u'전공': obj.get('major', ''),
            u'인터콥훈련여부': ','.join(obj.get('training', [])),
        }

        return func_map[label]

    def get_document(self, camp_idx, **kwargs):
        kwargs.pop('page', None)
        kwargs.pop('year', None)
        kwargs.pop('term', None)
        kwargs.pop('receptionmode', None)

        camp = Camp.get(camp_idx[0]) if type(camp_idx) is list else Camp.get(camp_idx)

        if camp.code == 'youth' or camp.code == 'kids':
            label_list = [
                u'이름', u'지부', u'참가구분', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'MIT', u'뉴커머',
                u'전체참석', u'인터콥훈련여부', u'등록날자', u'숙소', u'메모'
            ]
        else:
            label_list = [
                u'이름', u'지부', u'참가구분', u'출석', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'MIT', u'뉴커머',
                u'전체참석', u'오는날', u'가는날', u'직업', u'캠퍼스', u'전공', u'인터콥훈련여부', u'통역필요',
                u'등록날자', u'숙소', u'메모'
            ]

        member_list = Member.get_list(camp_idx, **kwargs)

        r = 0
        c = 0

        date_type_label = [
            u'오는날', u'가는날', u'등록날자'
        ]

        membership_type_label = [
            u'직업', u'캠퍼스', u'전공', u'인터콥훈련여부'
        ]

        for label in label_list:
            self.worksheet.write(r, c, label)
            c += 1
        r += 1

        for member in member_list:
            c = 0
            membership = member.get_membership_data()
            for label in label_list:
                if label in date_type_label:
                    self.worksheet.write_datetime(r, c, self.get_value(member, label), self.date_format)
                elif label in membership_type_label:
                    value = self.get_membership_value(membership, label)
                    self.worksheet.write(r, c, value)
                else:
                    self.worksheet.write(r, c, self.get_value(member, label))
                c += 1
            r += 1

        self.workbook.close()
        self.output.seek(0)

        return self.output


def get_document(camp_idx, **kwargs):
    kwargs.pop('page', None)
    member_list = Member.get_list(camp_idx, **kwargs)

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    r = 0
    c = 0
    label_list = [
        u'이름', u'지부', u'참가구분', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
        u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'MIT', u'뉴커머',
        u'전체참석', u'오는날', u'가는날', u'직업', u'캠퍼스', u'전공', u'인터콥훈련여부', u'통역필요',
        u'등록날자', u'숙소', u'메모'
    ]

    for label in label_list:
        worksheet.write(r, c, label)
        c += 1
    r += 1

    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    boolean = [u'아니오', u'예']

    for member in member_list:
        membership = member.get_membership_data()

        worksheet.write(r, 0, member.name)
        worksheet.write(r, 1, member.area.name)
        worksheet.write(r, 2, member.contact)
        worksheet.write(r, 3, member.church)
        worksheet.write(r, 4, member.birth)
        worksheet.write(r, 5, member.sex)
        worksheet.write(r, 6, boolean[member.bus_yn] if member.bus_yn is not None else '')
        worksheet.write(r, 7, boolean[member.mit_yn] if member.mit_yn is not None else '')
        worksheet.write(r, 8, boolean[member.newcomer_yn] if member.newcomer_yn is not None else '')
        worksheet.write(r, 9, boolean[member.fullcamp_yn] if member.fullcamp_yn is not None else '')
        worksheet.write_datetime(r, 10, member.date_of_arrival if member.date_of_arrival is not None else '', date_format)
        worksheet.write_datetime(r, 11, member.date_of_leave if member.date_of_leave is not None else '', date_format)
        worksheet.write(r, 12, membership['job'] if 'job' in membership else '')
        worksheet.write(r, 13, membership['campus'] if 'campus' in membership else '')
        worksheet.write(r, 14, membership['major'] if 'major' in membership else '')
        worksheet.write(r, 15, ','.join(membership['training']) if 'training' in membership else '')
        worksheet.write(r, 16, member.language if member.language is not None else '')
        worksheet.write_datetime(r, 17, member.regdate, date_format)
        worksheet.write(r, 18, member.memo)
        r += 1

    workbook.close()
    output.seek(0)

    return output


def get_old_document(member_list, db_type='mysql'):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    r = 0
    # c = 0

    worksheet.write(r, 0, u'캠프코드')
    worksheet.write(r, 1, u'출석여부')
    worksheet.write(r, 2, u'구분')
    worksheet.write(r, 3, u'이름')
    worksheet.write(r, 4, u'지부')
    worksheet.write(r, 5, u'성별')
    worksheet.write(r, 6, u'연락처')
    worksheet.write(r, 7, u'학교')
    worksheet.write(r, 8, u'전공/학년')
    worksheet.write(r, 9, u'교회')
    worksheet.write(r, 10, u'메모')
    worksheet.write(r, 11, u'선캠참석횟수')

    r += 1

    # date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

    if db_type == 'mysql':
        boolean = [u'아니오', u'예']

        for member in member_list:
            sch1 = ''
            sch2 = ''
            for membership in member.membership:
                if membership.key == 'sch1':
                    sch1 = membership.value
                elif membership.key == 'sch2':
                    sch2 = membership.value

            worksheet.write(r, 0, member.campcode)
            worksheet.write(r, 1, boolean[member.attend_yn])
            worksheet.write(r, 2, member.persontype)
            worksheet.write(r, 3, member.name)
            worksheet.write(r, 4, member.area.name)
            worksheet.write(r, 5, member.sex)
            worksheet.write(r, 6, member.contact)
            worksheet.write(r, 7, sch1)
            worksheet.write(r, 8, sch2)
            worksheet.write(r, 9, member.church)
            worksheet.write(r, 10, member.memo)
            worksheet.write(r, 11, member.count)
            r += 1

    elif db_type == 'mongo':
        boolean = {'N': u'아니오', 'Y': u'예'}

        for member in member_list:
            worksheet.write(r, 0, member['campcode'])
            worksheet.write(r, 1, boolean[member['entry']])
            worksheet.write(r, 2, member['camp'])
            worksheet.write(r, 3, member['name'])
            worksheet.write(r, 4, member['area'])
            worksheet.write(r, 5, member['sex'])
            worksheet.write(r, 6, member['hp1'])
            worksheet.write(r, 7, member['sch1'])
            worksheet.write(r, 8, member['sch2'])
            worksheet.write(r, 9, member['church'])
            worksheet.write(r, 10, member['memo'])
            worksheet.write(r, 11, member['count'])
            r += 1

    workbook.close()
    output.seek(0)

    return output
