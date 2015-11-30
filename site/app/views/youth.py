#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, session, flash, Blueprint
from core.functions import *
from core.functions.youth import *
from core.models import Promotion

context = Blueprint('youth', __name__, template_folder='templates', url_prefix='/youth')

def check_session(logintype):
    return True if not 'type' in session or session['type'] != logintype or not 'idx' in session else False

@context.route('/')
def home():
    return render_template('youth/home.html')


# 아이디 중복체크
@context.route('/individual/check-userid', methods=['POST'])
@context.route('/group/member/check-userid', methods=['POST'])
def check_userid():
    campidx = getCampIdx('youth')
    userid = request.form.get('userid')
    return "%d" % checkUserId(campidx, userid)

# 개인신청 - 신청서
@context.route('/individual/add')
def reg_individual():
    campidx = getCampIdx('youth')
    area_list = getAreaList('youth') # form에 들어갈 지부 목록
    #date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('youth/individual/add.html', camp='youth', campidx=campidx,
        area_list=area_list, group_yn=False)

# 개인신청 - 신청서를 데이터베이스에 저장
@context.route('/individual/add', methods=['POST'])
def reg_individual_proc():
    campidx = getCampIdx('youth')
    userid = request.form.get('userid', None)

    check = checkUserId(campidx, userid)
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('.reg_individual'))
    elif td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('.reg_individual'))
    else:
        member_idx = regIndividual(campidx, formData)

        session['type'] = u'개인'
        session['idx'] = member_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_individual'))

# 신청조회 - 로그인 폼
@context.route('/check')
def login():
    return render_template('youth/check.html')

@context.route('/check', methods=['POST'])
def login_proc():
    logintype = request.form.get('logintype', None)
    if logintype == '' or logintype == None:
        flash(u'신청 구분을 선택해주세요')
        return redirect(url_for('.login'))

    userid = request.form.get('userid', None)
    if userid == '' or userid == None:
        flash(u'아이디를 입력해주세요')
        return redirect(url_for('.login'))

    pwd = request.form.get('pwd', None)
    if pwd == '' or pwd == None:
        flash(u'비밀번호를 입력해 주세요')
        return redirect(url_for('.login'))

    campidx = getCampIdx('youth')
    if logintype == u'개인':
        if loginCheckUserid(campidx, userid, pwd):
            idx = getUserIdx(campidx, userid)
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('.show_individual'))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login'))
    elif logintype == u'단체':
        print loginCheckGroupid(campidx, userid, pwd)
        if loginCheckGroupid(campidx, userid, pwd):
            idx = getGroupIdx(campidx,userid)
            session['type'] = u'단체'
            session['idx'] = idx
            return redirect(url_for('.show_group'))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login'))
    else:
        flash('신청구분이 잘못되었습니다. 관리자에게 문의해주세요(070-8787-8870)')
        return redirect(url_for('.login'))

# 개인신청 조회
@context.route('/individual/info')
def show_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    idx = session['idx']
    member = getIndividualData(idx)
    area_name = getAreaName(member['area_idx'])
    return render_template('youth/individual/show.html', camp='cmc', member=member, area_name=area_name)

# 개인 신청 수정
@context.route('/individual/edit')
def edit_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    idx = session['idx']
    member = getIndividualData(idx)
    campidx = getCampIdx('youth')
    area_list = getAreaList('youth') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('youth/individual/edit.html', camp='youth', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 수정된 신청서 저장
@context.route('/individual/edit', methods=['POST'])
def edit_inidividual_proc():
    formData = getIndividualFormData()
    camp_idx = getCampIdx('youth')

    idx = session['idx']

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('.edit_individual', idx=idx))
    else:
        editIndividual(camp_idx, idx, formData)
        flash(u'신청서 수정이 완료되었습니다.')
        return redirect(url_for('.show_individual', idx=idx))

# 신청 취소
@context.route('/individual/cancel')
def cancel_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    return render_template('youth/individual/cancel.html')

# 신청 취소 적용
@context.route('/individual/cancel', methods=['POST'])
def cancel_individual_proc():
    cancel_reason = request.form.get('cancel_reason', None)
    idx = session['idx']
    cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.home'))

# 단체 아이디 중복체크
@context.route('/group/check-groupid', methods=['POST'])
def check_groupid():
    campidx = getCampIdx('youth')
    userid = request.form.get('groupid')
    return "%d" % checkGroupId(campidx, userid)

# 단체신청
@context.route('/group/add')
def reg_group():
    campidx = getCampIdx('youth')
    return render_template('youth/group/add.html', camp_idx=campidx, area_list=getAreaList('youth'))

# 단체신청 저장
@context.route('/group/add', methods=['POST'])
def reg_group_proc():
    campidx = getCampIdx('youth')
    groupid = request.form.get('groupid', None)

    check = checkGroupId(campidx, groupid)
    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('.reg_group'))

    else:
        formData = getGroupFormData()
        group_idx = regGroup(campidx, formData)

        session['type'] = u'단체'
        session['idx'] = group_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_group'))

# 단체신청 조회
@context.route('/group/info')
def show_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    group = getGroupData(idx)
    member_list = getMemberList(idx)
    return render_template('youth/group/show.html', group=group, area=getAreaName(group['area_idx']), member_list=member_list)

# 단체 수정
@context.route('/group/edit')
def edit_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    group = getGroupData(idx)
    campidx = getCampIdx('youth')
    area_list = getAreaList('youth') # form에 들어갈 지부 목록
    return render_template('youth/group/edit.html', group=group, area_list=area_list, campidx=campidx)

# 단체 수정 저장
@context.route('/group/edit', methods=['POST'])
def edit_group_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    formData = getGroupFormData()
    editGroup(idx, formData)
    flash(u"단체 정보 수정이 완료되었습니다.")
    return redirect(url_for('.show_group'))

# 단체 취소
@context.route('/group/cancel')
def cancel_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    return render_template('youth/group/cancel.html')

# 단체 취소 저장
@context.route('/group/cancel', methods=['POST'])
def cancel_group_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    cancel_reason = request.form.get('cancel_reason', None)
    cancelGroup(idx, cancel_reason)
    flash(u"단체 신청이 모두 취소되었습니다.")
    return redirect(url_for('.home'))


# 단체 멤버 추가
@context.route('/group/member/add')
def member_add():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('youth')
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('youth/individual/add.html', camp='cmc', campidx=campidx,
        date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 추가 적용
@context.route('/group/member/add', methods=['POST'])
def member_add_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('youth')
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('.member_add'))
    else:
        regIndividual(campidx, formData, idx)
        inc_mem_num(idx)
        flash(u'멤버 추가가 완료되었습니다.')
        return redirect(url_for('.show_group'))

# 단체 멤버 수정
@context.route('/group/member/edit/<member_idx>')
def member_edit(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('youth')
    member = getIndividualData(member_idx)
    area_list = getAreaList('youth') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('youth/individual/edit.html', camp='cmc', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 수정 저장
@context.route('/group/member/edit/<member_idx>', methods=['POST'])
def membet_edit_proc(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('youth')
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('.member_edit', member_idx=member_idx))
    else:
        editIndividual(campidx, member_idx, formData, idx)
        flash(u'신청서 수정이 완료되었습니다.')
        return redirect(url_for('.show_group'))

# 신청 취소
@context.route('/group/member/cancel/<member_idx>')
def member_cancel(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    return render_template('youth/individual/cancel.html')

# 신청 취소 적용
@context.route('/group/member/cancel/<member_idx>', methods=['POST'])
def member_cancel_proc(member_idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(member_idx, cancel_reason)
    idx = session['idx']
    dec_mem_num(idx)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.show_group'))

@context.route('/promotion', methods=['POST'])
def save_promotion_info():
    camp_idx = getCampIdx('youth')
    church_name = request.form.get('church_name', None)
    name = request.form.get('name', None)
    address = request.form.get('address', None)
    contact = request.form.get('contact', None)
    memo = request.form.get('memo', None)
    next_url = request.form.get('next', None)

    Promotion.insert(camp_idx, church_name, name, address, contact, memo)
    flash(u'홍보물 신청이 완료되었습니다')
    return redirect(url_for('.home'))

# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('.home'))
