'''
엑셀 다운로드 처리 모듈
'''
import datetime
import xlsxwriter

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO


def multi_getattr(obj, attr, default=None):
    '''
    getattr를 여러 계층으로 처리하기 위해 사용함
    '''
    attributes = attr.split(".")
    for att in attributes:
        try:
            obj = getattr(obj, att)
            if callable(obj):
                obj = obj()
        except AttributeError:
            return default
    return obj if obj is not None else default


class XlsxBuilder():
    '''
    xlsx 파일을 만들어주는 빌더 클래스
    '''
    def __init__(self):
        self.output = StringIO()
        self.workbook = xlsxwriter.Workbook(self.output)
        self.worksheet = self.workbook.add_worksheet()
        self.date_format = self.workbook.add_format({'num_format': 'yyyy-mm-dd'})

    @staticmethod
    def get_value(obj, label):
        '''
        column_name을 이용해 object에서 값을 받아옴. raw_value를 human_readable_value로 변환
        '''
        boolean = [u'아니오', u'예', u'??']
        ox_ = ['X', 'O', '??']
        sex = {'M': u'남', 'F': u'여', '': u'오류(미입력)'}
        complete = [u'미납', u'부분납', u'완납']
        func_map = {
            u'이름': multi_getattr(obj, 'name', ''),
            u'지부': multi_getattr(obj, 'area.name', ''),
            u'참가구분': multi_getattr(obj, 'persontype', ''),
            u'출석': ox_[multi_getattr(obj, 'attend_yn', 0)],
            u'단체': multi_getattr(obj, 'group.name', ''),
            u'성별': sex[multi_getattr(obj, 'sex', '')],
            u'연락처': multi_getattr(obj, 'contact', ''),
            u'입금상태': complete[multi_getattr(obj, 'payment.complete', 0)],
            u'입금액': multi_getattr(obj, 'payment.amount', ''),
            u'재정클레임': multi_getattr(obj, 'payment.claim', ''),
            u'출석교회': multi_getattr(obj, 'church', ''),
            u'생년월일': multi_getattr(obj, 'birth', ''),
            u'단체버스': boolean[multi_getattr(obj, 'bus_yn', 0)],
            u'2017FO/MIT': boolean[multi_getattr(obj, 'mit_yn', 0)],
            u'2017MIT': boolean[multi_getattr(obj, 'mit_yn', 0)],
            u'뉴커머': boolean[multi_getattr(obj, 'newcomer_yn', 0)],
            u'전체참석': boolean[multi_getattr(obj, 'fullcamp_yn', 0)],
            u'오는날': multi_getattr(obj, 'date_of_arrival', 0),
            u'가는날': multi_getattr(obj, 'date_of_leave', 0),
            u'통역필요': multi_getattr(obj, 'language', ''),
            u'등록날자': multi_getattr(obj, 'regdate', 0),
            u'숙소': ''.join([multi_getattr(obj, 'room.building', ''), \
            multi_getattr(obj, 'room.number', '')]),
            u'메모': multi_getattr(obj, 'memo', ''),
        }

        return func_map[label]


    @staticmethod
    def get_membership_value(obj, label):
        '''
        가변필드의 값을 받아오기 위해 처리해줌
        '''
        boolean = [u'아니오', u'예', u'??']
        func_map = {
            u'직업': obj.get('job', ''),
            u'직분': obj.get('job', ''),
            u'직장명': obj.get('job_name', ''),
            u'캠퍼스': obj.get('campus', ''),
            u'전공': obj.get('major', ''),
            u'인터콥훈련여부': ','.join(obj.get('training', [])),
            u'비전스쿨': boolean[int(obj.get('vision_yn', '0') \
            if obj.get('vision_yn', '0') not in [None, 'none', 'None'] else 0)],
        }

        return func_map[label]

    def get_document(self, campcode, member_list):
        '''
        멤버 리스트 객체를 받아서 엑셀 문서로 변환해줌
        '''

        if campcode in ['youth', 'kids']:
            label_list = [
                u'이름', u'지부', u'참가구분', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'2017MIT', u'뉴커머',
                u'전체참석', u'인터콥훈련여부', u'등록날자', u'숙소', u'메모'
            ]
        elif campcode == 'cmc':
            label_list = [
                u'이름', u'지부', u'참가구분', u'출석', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'2017FO/MIT', u'뉴커머', u'비전스쿨',
                u'전체참석', u'오는날', u'가는날', u'직업', u'캠퍼스', u'전공', u'인터콥훈련여부', u'통역필요',
                u'등록날자', u'숙소', u'메모'
            ]
        elif campcode == 'cbtj':
            label_list = [
                u'이름', u'지부', u'참가구분', u'출석', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'2017FO/MIT', u'뉴커머', u'비전스쿨',
                u'전체참석', u'오는날', u'가는날', u'직업', u'직장명', u'인터콥훈련여부', u'통역필요',
                u'등록날자', u'숙소', u'메모'
            ]
        else:  # 여남시
            label_list = [
                u'이름', u'지부', u'참가구분', u'출석', u'단체', u'성별', u'연락처', u'입금상태', u'입금액',
                u'재정클레임', u'출석교회', u'생년월일', u'단체버스', u'2017FO/MIT', u'뉴커머',
                u'전체참석', u'오는날', u'가는날', u'직분', u'인터콥훈련여부', u'통역필요',
                u'등록날자', u'숙소', u'메모'
            ]

        row = 0
        col = 0

        date_type_label = [
            u'오는날', u'가는날', u'등록날자'
        ]

        membership_type_label = [
            u'직업', u'캠퍼스', u'전공', u'인터콥훈련여부', u'비전스쿨', u'직분', u'직장명'
        ]

        for label in label_list:
            self.worksheet.write(row, col, label)
            col += 1
        row += 1

        for member in member_list:
            col = 0
            membership = member.get_membership_data()
            for label in label_list:
                if label in date_type_label:
                    if isinstance(self.get_value(member, label), datetime.datetime) \
                    or isinstance(self.get_value(member, label), datetime.date):
                        self.worksheet.write_datetime(row, col, self.get_value(member, \
                        label), self.date_format)
                    else:
                        self.worksheet.write(row, col, "")
                elif label in membership_type_label:
                    value = self.get_membership_value(membership, label)
                    self.worksheet.write(row, col, value)
                else:
                    self.worksheet.write(row, col, self.get_value(member, label))
                col += 1
            row += 1

        self.workbook.close()
        self.output.seek(0)

        return self.output
