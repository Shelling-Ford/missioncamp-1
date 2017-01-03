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


def map_to_str(_map, param):
    if type(_map) is dict:
        for key, value in _map.items():
            if param == key:
                return value
    if type(_map) is list:
        for key, value in enumerate(_map):
            if param == key:
                return value
    return "ERROR({})".format(param)


def boolean_to_str(param):
    return map_to_str(['아니오', '예'], param)


def boolean_to_ox(param):
    return map_to_str(['X', 'O'], param)


def sex_to_str(param):
    return map_to_str({'M': '남', 'F': '여'}, param)


def complete_to_str(param):
    return map_to_str(['미납', '부분납', '완납'], param)


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
        func_map = {
            '이름': multi_getattr(obj, 'name', ''),
            '지부': multi_getattr(obj, 'area.name', ''),
            '참가구분': multi_getattr(obj, 'persontype', ''),
            '출석': boolean_to_ox(multi_getattr(obj, 'attend_yn', 0)),
            '단체': multi_getattr(obj, 'group.name', ''),
            '성별': sex_to_str(multi_getattr(obj, 'sex', '')),
            '연락처': multi_getattr(obj, 'contact', ''),
            '입금상태': complete_to_str(multi_getattr(obj, 'payment.complete', 0)),
            '입금액': multi_getattr(obj, 'payment.amount', ''),
            '재정클레임': multi_getattr(obj, 'payment.claim', ''),
            '출석교회': multi_getattr(obj, 'church', ''),
            '생년월일': multi_getattr(obj, 'birth', ''),
            '단체버스': boolean_to_str(multi_getattr(obj, 'bus_yn', 0)),
            '2017FO/MIT': boolean_to_str(multi_getattr(obj, 'mit_yn', 0)),
            '2017MIT': boolean_to_str(multi_getattr(obj, 'mit_yn', 0)),
            '뉴커머': boolean_to_str(multi_getattr(obj, 'newcomer_yn', 0)),
            '전체참석': boolean_to_str(multi_getattr(obj, 'fullcamp_yn', 0)),
            '오는날': multi_getattr(obj, 'date_of_arrival', 0),
            '가는날': multi_getattr(obj, 'date_of_leave', 0),
            '통역필요': multi_getattr(obj, 'language', ''),
            '등록날자': multi_getattr(obj, 'regdate', 0),
            '숙소': ''.join([multi_getattr(obj, 'room.building', ''), multi_getattr(obj, 'room.number', '')]),
            '메모': multi_getattr(obj, 'memo', ''),
        }

        return func_map[label]

    @staticmethod
    def get_membership_value(obj, label):
        '''
        가변필드의 값을 받아오기 위해 처리해줌
        '''
        boolean = ['아니오', '예', '??']
        func_map = {
            '직업': obj.get('job', ''),
            '직분': obj.get('job', ''),
            '직장명': obj.get('job_name', ''),
            '캠퍼스': obj.get('campus', ''),
            '전공': obj.get('major', ''),
            '인터콥훈련여부': ','.join(obj.get('training', [])),
            '비전스쿨': boolean_to_str(int(obj.get('vision_yn', '0') if obj.get('vision_yn', '0') not in [None, 'none', 'None'] else 0)),
        }

        return func_map[label]

    def get_document(self, campcode, member_list):
        '''
        멤버 리스트 객체를 받아서 엑셀 문서로 변환해줌
        '''
        label_list = [
            '이름', '지부', '참가구분', '출석', '단체', '성별', '연락처', '입금상태', '입금액',
            '재정클레임', '출석교회', '생년월일', '단체버스', '2017MIT', '뉴커머',
        ]

        if campcode in ['youth', 'kids']:
            label_list.extend([
                '전체참석', '오는날', '가는날', '인터콥훈련여부', '등록날자', '숙소', '메모'
            ])
        elif campcode == 'cmc':
            label_list.extend([
                '비전스쿨',
                '전체참석', '오는날', '가는날', '직업', '캠퍼스', '전공', '인터콥훈련여부', '통역필요',
                '등록날자', '숙소', '메모'
            ])
        elif campcode == 'cbtj':
            label_list.extend([
                '비전스쿨',
                '전체참석', '오는날', '가는날', '직업', '직장명', '인터콥훈련여부', '통역필요',
                '등록날자', '숙소', '메모'
            ])
        else:  # 여남시
            label_list.extend([
                '전체참석', '오는날', '가는날', '직분', '인터콥훈련여부', '통역필요',
                '등록날자', '숙소', '메모'
            ])

        row = 0
        col = 0

        date_type_label = [
            '오는날', '가는날', '등록날자'
        ]

        membership_type_label = [
            '직업', '캠퍼스', '전공', '인터콥훈련여부', '비전스쿨', '직분', '직장명'
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
                    if isinstance(self.get_value(member, label), datetime.datetime) or isinstance(self.get_value(member, label), datetime.date):
                        self.worksheet.write_datetime(row, col, self.get_value(member, label), self.date_format)
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
