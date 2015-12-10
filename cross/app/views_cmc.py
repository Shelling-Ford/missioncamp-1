#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint, abort
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.functions import *
from core.functions.cmc import *
from core.models import Group, Member, Camp, Area, Room, Payment

from functions import *
import functions_mongo as mongo
import functions_xlsx as xlsx
import xlsxwriter

# Blueprint 초기화
cmc = Blueprint('cmc', __name__, template_folder='templates', url_prefix='/cmc')

master_permission = Permission(RoleNeed('master'))
hq_permission = Permission(RoleNeed('hq'))
branch_permission = Permission(RoleNeed('branch'))
cmc_permission = Permission(RoleNeed('cmc'))

# 메인 통계
@cmc.route('/')
@login_required
@branch_permission.require(http_exception=403)
def home():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))
    camp_idx = Camp.get_idx('cmc', year, term)
    stat = get_basic_stat(camp_idx)
    return render_template('cmc/home.html', stat=stat)

# 신청자 목록
@cmc.route('/list')
@login_required
@branch_permission.require(http_exception=403)
def member_list():
    camp_idx = Camp.get_idx('cmc')
    group_idx = request.args.get('group_idx', None)
    page = int(request.args.get('page', 1))
    group = Group.get(group_idx) if group_idx is not None else None
    member_list = Member.get_list(camp_idx, **request.args.to_dict())
    count = Member.count(camp_idx, **request.args.to_dict())
    return render_template('cmc/list.html', members=member_list, group=group, count=count-(page-1)*50, nav=range(1, int(count/50)+2))

# 신청자 상세
@cmc.route('/member')
@login_required
@branch_permission.require(http_exception=403)
def member():
    camp_idx = Camp.get_idx('cmc')

    member_idx = request.args.get('member_idx', 0)

    if member_idx != 0:
        member = Member.get(member_idx)
        room_list = Room.get_list()
        area_list = Area.get_list('cmc')
        group_list = Group.get_list(camp_idx)

        return render_template('cmc/member.html', member=member, room_list=room_list, area_list=area_list, group_list=group_list)
    else:
        abort(404)

# 입금 정보 입력
@cmc.route('/pay', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def pay():
    member_idx = request.args.get('member_idx', 0)
    amount = request.form.get('amount')
    complete = request.form.get('complete')
    claim = request.form.get('claim')
    paydate = request.form.get('paydate')
    staff_name = request.form.get('staff_name')

    Payment.save(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)
    return redirect(url_for('.member', member_idx=member_idx))

# 입금 정보 삭제
@cmc.route('/delpay')
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def delpay():
    member_idx = request.args.get('member_idx', 0)
    Payment.delete(member_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 숙소 정보 입력
@cmc.route('/room_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def room_setting():
    member_idx = request.form.get('member_idx', 0)
    room_idx = request.form.get('idx', 0)
    Member.update(member_idx=member_idx, room_idx=room_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 지부 변경
@cmc.route('/area_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def area_setting():
    member_idx = request.form.get('member_idx', 0)
    area_idx = request.form.get('area_idx', 0)
    Member.update(member_idx=member_idx, area_idx=area_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 단체 변경
@cmc.route('/group_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def group_setting():
    member_idx = request.form.get('member_idx', 0)
    group_idx = request.form.get('group_idx', 0)
    Member.update(member_idx=member_idx, group_idx=group_idx)
    return redirect(url_for('.member', member_idx=member_idx))

@cmc.route('/excel-down', methods=['GET'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def excel_down():
    camp_idx = getCampIdx('cmc')
    output = xlsx.get_document(camp_idx, **request.args)
    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
    return response

#**수정필요!!
# 개인 신청 수정
@cmc.route('/member-edit')
@login_required
@branch_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def member_edit():
    idx = request.args.get('member_idx', 0)
    session['idx'] = idx
    member = getIndividualData(idx)

    group_yn = member['group_idx'] is not None

    campidx = getCampIdx('cmc')
    area_list = getAreaList('cmc') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('cmc/member_edit.html', camp='cmc', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=group_yn)

#**수정필요!!
# 수정된 신청서 저장
@cmc.route('/member-edit', methods=['POST'])
@login_required
@branch_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def member_edit_proc():
    formData = getIndividualFormData()
    camp_idx = getCampIdx('cmc')

    idx = session['idx']

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('.member_edit', idx=idx))
    else:
        editIndividual(camp_idx, idx, formData)
        flash(u'신청서 수정이 완료되었습니다.')
        return redirect(url_for('.member', member_idx=idx))


# 신청 취소
@cmc.route('/member-cancel')
@login_required
@branch_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def member_cancel():
    member_idx = request.args.get('member_idx', 0)
    session['idx'] = member_idx

    return render_template('cmc/member_cancel.html')

# 신청 취소 적용
@cmc.route('/member-cancel', methods=['POST'])
@login_required
@branch_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def member_cancel_proc():
    cancel_reason = request.form.get('cancel_reason', None)
    idx = session['idx']
    Member.update(idx, cancel_yn=1, cancel_reason=cancel_reason)
    #cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.member_list'))

# 신청 취소 복원
@cmc.route('/member-recover')
@login_required
@branch_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def member_recover():
    member_idx = request.args.get('member_idx')
    Member.update(member_idx, cancel_yn=0)
    flash(u'신청이 복원되었습니다')
    return redirect(url_for('.member_list'))

# 이전 참가자 리스트
@cmc.route('/old-list')
@login_required
@branch_permission.require(http_exception=403)
def old_list():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    skip = int(request.args.get('page', 1)) * 50 - 50
    name = request.args.get('name', None)
    area = request.args.get('area', None)
    camp = request.args.get('camp', 'cmc')

    if year == 0 or term == 0:
        camp = None if camp == 'cmc' else camp
        campcode = request.args.get('campcode', None)
        member_list = mongo.get_member_list_with_count(skip=skip, campcode=campcode, name=name, area=area, camp=camp)
        count = mongo.get_member_count(campcode=campcode, name=name, area=area, camp=camp)
        return render_template("cmc/old_list.html", members=member_list, name=name, area=area, campcode=campcode, count=range(1, int(count/50)+2))
    else:
        camp_idx = Camp.get_idx(camp, year, term)
        area_idx = request.args.get('area_idx', None)
        member_list = Member.get_old_list(camp_idx=camp_idx, name=name, offset=skip, area_idx=area_idx)
        member_count = Member.count(camp_idx=camp_idx, name=name, area_idx=area_idx)

        for member in member_list:
            count = mongo.db.count({"hp1": member.contact, "name":member.name, "entry":"Y", "fin":{"$ne":"d"}})
            count += Member.count(camp_idx=camp_idx, name=member.name, contact=member.contact, attend_yn=1, cancel_yn=0)
            setattr(member, 'count', count)

        return render_template("cmc/old_list_2.html", members=member_list, camp=camp, year=year, term=term, name=name, count=range(1, int(member_count/50)+2))



# 이전 참가자 상세
@cmc.route('/old-member')
@login_required
@branch_permission.require(http_exception=403)
def old_member():
    name = request.args.get('name', None)
    hp1 = request.args.get('hp1', None)

    if name is not None and hp1 is not None:
        member_list = mongo.get_member_list(name=name, hp1=hp1)
        logs = mongo.get_member_call_logs(name=name, hp1=hp1)

    return render_template("cmc/old_member.html", name=name, hp1=hp1, members=member_list, logs=logs)

# 통화내용 저장
@cmc.route('/save-log', methods=['POST'])
@login_required
@branch_permission.require(http_exception=403)
def save_log():
    name = request.form.get('name', None)
    hp1 = request.form.get('hp1', None)
    log = request.form.get('log', None)
    date = datetime.datetime.today()

    mongo.save_member_call_log(name=name, hp1=hp1, log=log, date=date)
    return redirect(url_for('.old_member', name=name, hp1=hp1))

# 이전 통계
@cmc.route('/old-stat')
@login_required
@branch_permission.require(http_exception=403)
def old_stat():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        campcode = request.args.get('campcode', None)
        stat = mongo.get_basic_stat(campcode)
        return render_template('cmc/old_stat.html', stat=stat, campcode=campcode)
    else:
        camp_idx = getCampIdx('cmc', year, term)
        stat = get_basic_stat(camp_idx)
        return render_template('cmc/old_stat_2.html', stat=stat, year=year, term=term)

# 엑셀 다운로드
@cmc.route('/old-excel-down', methods=['GET'])
@login_required
@hq_permission.require(http_exception=403)
@cmc_permission.require(http_exception=403)
def old_excel_down():

    name = request.args.get('name', None)
    area = request.args.get('area', None)
    camp = request.args.get('camp', None)
    campcode = request.args.get('campcode', None)


    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    try:
        import cStringIO as StringIO
    except:
        import StringIO

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    r = 0
    c = 0

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

    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

    if year == 0 or term == 0:
        campcode = request.args.get('campcode', None)
        member_list = mongo.get_member_list_with_count(campcode=campcode, name=name, area=area, camp=camp)

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

    else:
        camp_idx = getCampIdx(camp, year, term)
        area_idx = request.args.get('area_idx', None)
        member_list = Member.get_old_list(camp_idx=camp_idx, name=name, area_idx=area_idx)

        boolean = [u'아니오', u'예']

        for member in member_list:
            count = mongo.db.count({"hp1": member.contact, "name":member.name, "entry":"Y", "fin":{"$ne":"d"}})
            count += Member.count(camp_idx=camp_idx, name=member.name, contact=member.contact, attend_yn=1, cancel_yn=0)
            setattr(member, 'count', count)

            sch1 = ''
            sch2 = ''
            for membership in member.membership:
                if membership.key == 'sch1':
                    sch1 = membership.value
                elif membership.key == 'sch2':
                    sch2 = membership.value

            worksheet.write(r, 0, "%s_%d_%d" % (camp, year, term))
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

    workbook.close()

    output.seek(0)
    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
    return response

@cmc.errorhandler(403)
def forbidden(e):
    flash(u'권한이 없습니다.')
    return redirect(url_for('.home', next=request.url))
