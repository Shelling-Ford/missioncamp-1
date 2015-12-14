# -*-coding:utf-8-*-
import xlsxwriter
from core.models import Member

try:
    import cStringIO as StringIO
except:
    import StringIO


def get_document(camp_idx, **kwargs):
    kwargs.pop('page', None)
    member_list = Member.get_list(camp_idx, **kwargs)

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    r = 0
    # c = 0
    worksheet.write(r, 0, u'이름')
    worksheet.write(r, 1, u'지부')
    worksheet.write(r, 2, u'연락처')
    worksheet.write(r, 3, u'출석교회')
    worksheet.write(r, 4, u'생년월일')
    worksheet.write(r, 5, u'성별')
    worksheet.write(r, 6, u'단체버스')
    worksheet.write(r, 7, u'MIT')
    worksheet.write(r, 8, u'선캠뉴커머')
    worksheet.write(r, 9, u'전체참석')
    worksheet.write(r, 10, u'캠프도착')
    worksheet.write(r, 11, u'귀가')
    worksheet.write(r, 12, u'직업')
    worksheet.write(r, 13, u'캠퍼스')
    worksheet.write(r, 14, u'전공')
    worksheet.write(r, 15, u'인터콥 훈련 여부')
    worksheet.write(r, 16, u'통역필요')
    worksheet.write(r, 17, u'등록날자')
    worksheet.write(r, 18, u'메모')
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
        boolean = {'N':u'아니오', 'Y':u'예'}

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


