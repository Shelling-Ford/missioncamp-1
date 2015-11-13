#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask.helpers import make_response
from jinja2 import TemplateNotFound
from core.functions import *
from core.functions.cmc import *
from functions import *
import functions_mongo as mongo
import xlsxwriter

cmc = Blueprint('cmc', __name__, template_folder='templates', url_prefix='/cmc')

@cmc.route('/')
def home():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = getCampIdx('cmc')
    else:
        camp_idx = getCampIdx('cmc', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('cmc/home.html', stat=stat)

@cmc.route('/list')
def member_list():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)
    member_name = request.args.get('name', None)

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name)
    return render_template('cmc/list.html', members=member_list, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name)

@cmc.route('/member')
def member():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')

    member_idx = request.args.get('member_idx', 0)

    if member_idx != 0:
        member = get_member(member_idx)
        member['membership'] = get_membership(member_idx)
        payment = get_payment(member_idx)
        room_list = get_room_list()
        area_name = getAreaName(member['area_idx'])

    return render_template('cmc/member.html', member=member, payment=payment, role=session['role'], rooms=room_list, area_name=area_name)

@cmc.route('/pay', methods=['POST'])
def pay():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    member_idx = request.args.get('member_idx', 0)
    amount = request.form.get('amount')
    complete = request.form.get('complete')
    claim = request.form.get('claim')
    paydate = request.form.get('paydate')
    staff_name = request.form.get('staff_name')

    save_payment(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)
    return redirect(url_for('.member', member_idx=member_idx))

@cmc.route('/delpay')
def delpay():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    member_idx = request.args.get('member_idx', 0)
    delete_payment(member_idx)
    return redirect(url_for('.member', member_idx=member_idx))

@cmc.route('/room_setting', methods=['POST'])
def room_setting():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    member_idx = request.form.get('member_idx', 0)
    room_idx = request.form.get('idx', 0)
    set_member_room(member_idx=member_idx, room_idx=room_idx)
    return redirect(url_for('.member', member_idx=member_idx))

@cmc.route('/excel-down', methods=['GET'])
def excel_down():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')

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
@cmc.route('/member-edit')
def member_edit():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    idx = request.args.get('member_idx', 0)
    session['idx'] = idx
    member = getIndividualData(idx)
    campidx = getCampIdx('cmc')
    area_list = getAreaList('cmc') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('cmc/member_edit.html', camp='cmc', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 수정된 신청서 저장
@cmc.route('/member-edit', methods=['POST'])
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
def member_cancel():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    member_idx = request.args.get('member_idx', 0)
    session['idx'] = member_idx

    return render_template('cmc/member_cancel.html')

# 신청 취소 적용
@cmc.route('/member-cancel', methods=['POST'])
def member_cancel_proc():
    cancel_reason = request.form.get('cancel_reason', None)
    idx = session['idx']
    cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.member_list'))

@cmc.route('/old-list')
def old_list():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    #campcode = request.args.get('campcode', None)

    #if campcode is not None:
    member_list = mongo.get_member_by_contact()

    return render_template("cmc/old_list.html", members=member_list)

@cmc.route('/old-member')
def old_member():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    name = request.args.get('name', None)
    hp1 = request.args.get('hp1', None)

    if name is not None and hp1 is not None:
        member_list = mongo.get_member_list(name=name, hp1=hp1)
    return render_template("cmc/old_member.html", name=name, hp1=hp1, members=member_list)
