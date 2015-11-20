#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.functions import *
from core.functions.ws import *
from functions import *
import functions_mongo as mongo
import xlsxwriter

# Blueprint 초기화
ws = Blueprint('ws', __name__, template_folder='templates', url_prefix='/ws')

master_permission = Permission(RoleNeed('master'))
hq_permission = Permission(RoleNeed('hq'))
branch_permission = Permission(RoleNeed('branch'))
ws_permission = Permission(RoleNeed('ws'))

# 메인 통계
@ws.route('/')
@login_required
@branch_permission.require(http_exception=403)
def home():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = getCampIdx('ws')
    else:
        camp_idx = getCampIdx('ws', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('ws/home.html', stat=stat)

from core.models import Group
# 신청자 목록
@ws.route('/list')
@login_required
@branch_permission.require(http_exception=403)
def member_list():
    camp_idx = getCampIdx('ws')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)
    group_idx = request.args.get('group_idx', None)

    if group_idx is not None:
        group = Group.get(group_idx)
    else:
        group = None

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, group_idx=group_idx)
    return render_template('ws/list.html', members=member_list, group=group)

# 신청자 상세
@ws.route('/member')
@login_required
@branch_permission.require(http_exception=403)
def member():
    camp_idx = getCampIdx('ws')

    member_idx = request.args.get('member_idx', 0)

    if member_idx != 0:
        member = get_member(member_idx)
        member['membership'] = get_membership(member_idx)
        payment = get_payment(member_idx)
        room_list = get_room_list()
        area_name = getAreaName(member['area_idx'])

    return render_template('ws/member.html', member=member, payment=payment, role=current_user.role, rooms=room_list, area_name=area_name)

# 입금 정보 입력
@ws.route('/pay', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def pay():
    member_idx = request.args.get('member_idx', 0)
    amount = request.form.get('amount')
    complete = request.form.get('complete')
    claim = request.form.get('claim')
    paydate = request.form.get('paydate')
    staff_name = request.form.get('staff_name')

    save_payment(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)
    return redirect(url_for('.member', member_idx=member_idx))

# 입금 정보 삭제
@ws.route('/delpay')
@login_required
@hq_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def delpay():
    member_idx = request.args.get('member_idx', 0)
    delete_payment(member_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 숙소 정보 입력
@ws.route('/room_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def room_setting():
    member_idx = request.form.get('member_idx', 0)
    room_idx = request.form.get('idx', 0)
    set_member_room(member_idx=member_idx, room_idx=room_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 엑셀 다운로드
@ws.route('/excel-down', methods=['GET'])
@login_required
@hq_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def excel_down():
    camp_idx = getCampIdx('ws')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)
    member_name = request.args.get('name', None)

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name)

    try:
        import cStringIO as StringIO
    except:
        import StringIO

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.set_column('C:C', 15)
    worksheet.set_column('E:E', 10)
    worksheet.set_column('F:F', 8)
    worksheet.set_column('G:G', 8)
    worksheet.set_column('H:H', 8)
    worksheet.set_column('I:I', 8)
    worksheet.set_column('J:J', 8)
    worksheet.set_column('K:K', 10)
    worksheet.set_column('L:L', 10)
    worksheet.set_column('M:M', 15)
    worksheet.set_column('P:P', 20)
    worksheet.set_column('R:R', 10)
    worksheet.set_column('S:S', 20)


    r = 0
    c = 0
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
        worksheet.write(r, 0, member['name'])
        worksheet.write(r, 1, member['area'])
        worksheet.write(r, 2, member['contact'])
        worksheet.write(r, 3, member['church'])
        worksheet.write(r, 4, member['birth'])
        worksheet.write(r, 5, member['sex'])
        worksheet.write(r, 6, boolean[member['bus_yn']])
        worksheet.write(r, 7, boolean[member['mit_yn']])
        worksheet.write(r, 8, boolean[member['newcomer_yn']])
        worksheet.write(r, 9, boolean[member['fullcamp_yn']])
        worksheet.write_datetime(r, 10, member['date_of_arrival'], date_format)
        worksheet.write_datetime(r, 11, member['date_of_leave'], date_format)
        if 'membership' in member and 'job' in member['membership']:
            worksheet.write(r, 12, member['membership']['job'])
        if 'membership' in member and 'campus' in member['membership']:
            worksheet.write(r, 13, member['membership']['campus'])
        if 'membership' in member and 'major' in member['membership']:
            worksheet.write(r, 14, member['membership']['major'])
        if 'membership' in member and 'training' in member['membership']:
            s = ""
            for t in member['membership']['training']:
                s += '%s,' % t
            worksheet.write(r, 15, s)
        worksheet.write(r, 16, member['language'])
        worksheet.write_datetime(r, 17, member['regdate'], date_format)
        worksheet.write(r, 18, member['memo'])
        r += 1

    workbook.close()

    output.seek(0)
    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
    return response

# 개인 신청 수정
@ws.route('/member-edit')
@login_required
@branch_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def member_edit():
    idx = request.args.get('member_idx', 0)
    session['idx'] = idx
    member = getIndividualData(idx)
    campidx = getCampIdx('ws')
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록

    group_yn = member['group_idx'] is not None

    return render_template('ws/member_edit.html', camp='ws', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=group_yn)

# 수정된 신청서 저장
@ws.route('/member-edit', methods=['POST'])
@login_required
@branch_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def member_edit_proc():
    formData = getIndividualFormData()
    camp_idx = getCampIdx('ws')

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
@ws.route('/member-cancel')
@login_required
@branch_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def member_cancel():
    member_idx = request.args.get('member_idx', 0)
    session['idx'] = member_idx

    return render_template('ws/member_cancel.html')

# 신청 취소 적용
@ws.route('/member-cancel', methods=['POST'])
@login_required
@branch_permission.require(http_exception=403)
@ws_permission.require(http_exception=403)
def member_cancel_proc():
    cancel_reason = request.form.get('cancel_reason', None)
    idx = session['idx']
    cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.member_list'))

# 이전 참가자 리스트
@ws.route('/old-list')
@login_required
@branch_permission.require(http_exception=403)
def old_list():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    skip = int(request.args.get('page', 0)) * 40
    name = request.args.get('name', None)
    area = request.args.get('area', None)
    camp = request.args.get('camp', None)

    if year == 0 or term == 0:
        campcode = request.args.get('campcode', None)
        member_list = mongo.get_member_list_with_count(skip=skip, campcode=campcode, name=name, area=area, camp=camp)
        count = mongo.get_member_count(campcode=campcode, name=name, area=area, camp=camp)

    else:
        camp_idx = getCampIdx('ws', year, term)
        #member_list = mongo.get_member_list(campcode=campcode)

    return render_template("ws/old_list.html", members=member_list, area=area, campcode=campcode, count=range(1, int(count/40)))

# 이전 참가자 상세
@ws.route('/old-member')
@login_required
@branch_permission.require(http_exception=403)
def old_member():
    name = request.args.get('name', None)
    hp1 = request.args.get('hp1', None)

    if name is not None and hp1 is not None:
        member_list = mongo.get_member_list(name=name, hp1=hp1)
        logs = mongo.get_member_call_logs(name=name, hp1=hp1)

    return render_template("ws/old_member.html", name=name, hp1=hp1, members=member_list, logs=logs)

# 통화내용 저장
@ws.route('/save-log', methods=['POST'])
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
@ws.route('/old-stat')
@login_required
@branch_permission.require(http_exception=403)
def old_stat():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        campcode = request.args.get('campcode', None)
        stat = mongo.get_basic_stat(campcode)
        return render_template('ws/old_stat.html', stat=stat, campcode=campcode)
    else:
        camp_idx = getCampIdx('ws', year, term)
        stat = get_basic_stat(camp_idx)
        return render_template('ws/old_stat_2.html', stat=stat, year=year, term=term)

@ws.errorhandler(403)
def forbidden(e):
    flash(u'권한이 없습니다.')
    return redirect(url_for('.home', next=request.url))
