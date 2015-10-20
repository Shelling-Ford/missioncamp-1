#-*-coding:utf-8-*-
from app import context
from flask import render_template, flash, redirect, url_for, session, request
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *

# camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
def check_campcode(camp):
    if camp != 'cbtj' and camp != 'cbtj2':
        print u'잘못된 접근: 캠프코드가 cbtj 또는 cbtj2가 아닙니다.'
        raise BaseException

def check_session(camp, logintype, idx=None):
    return True if not 'type' in session or session['type'] != logintype or not 'idx' in session else False

@context.route('/')
def home():
    return render_template('home.html')

@context.route('/<page>')
def page(page):
    try:
        return render_template('/%s.html' % page)
    except TemplateNotFound:
        return render_template('/404.html')

@context.route('/<camp>/')
def camp(camp):
    return render_template('%s/home.html' % camp)

# 아이디 중복체크
@context.route('/<camp>/check-userid', methods=['POST'])
def check_userid(camp):
    campidx = getCampIdx(camp)
    userid = request.form.get('userid')
    return "%d" % checkUserId(campidx, userid)

# 개인신청 - 신청서
@context.route('/<camp>/individual/add')
def reg_individual(camp):
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    area_list = getAreaList('cbtj') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('%s/individual/add.html' % camp, camp=camp, campidx=campidx,
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 개인신청 - 신청서를 데이터베이스에 저장
@context.route('/<camp>/individual/add', methods=['POST'])
def reg_individual_proc(camp):
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    userid = request.form.get('userid', None)

    check = checkUserId(campidx, userid)
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('reg_individual', camp=camp))
    elif td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('reg_individual', camp=camp))
    else:
        member_idx = regIndividual(campidx, formData)

        session['type'] = u'개인'
        session['idx'] = member_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('show_individual', camp=camp))

# 신청조회 - 로그인 폼
@context.route('/<camp>/check')
def login(camp):
    return render_template('%s/check.html' % camp)

@context.route('/<camp>/check', methods=['POST'])
def login_proc(camp):
    logintype = request.form.get('logintype', None)
    if logintype == '' or logintype == None:
        flash(u'신청 구분을 선택해주세요')
        return redirect(url_for('login', camp=camp))

    userid = request.form.get('userid', None)
    if userid == '' or userid == None:
        flash(u'아이디를 입력해주세요')
        return redirect(url_for('login', camp=camp))

    pwd = request.form.get('pwd', None)
    if pwd == '' or pwd == None:
        flash(u'비밀번호를 입력해 주세요')
        return redirect(url_for('login', camp=camp))

    campidx = getCampIdx(camp)
    if logintype == u'개인':
        if loginCheckUserid(campidx, userid, pwd):
            idx = getUserIdx(campidx, userid)
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('show_individual', camp=camp, idx=idx))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('login', camp=camp))
    elif logintype == u'단체':
        print loginCheckGroupid(campidx, userid, pwd)
        if loginCheckGroupid(campidx, userid, pwd):
            idx = getGroupIdx(campidx,userid)
            session['type'] = u'단체'
            session['idx'] = idx
            return redirect(url_for('show_group', camp=camp))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('login', camp=camp))
    else:
        flash('신청구분이 잘못되었습니다. 관리자에게 문의해주세요(070-8787-8870)')
        return redirect(url_for('login', camp=camp))

# 개인신청 조회
@context.route('/<camp>/individual/<idx>')
def show_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))

    member = getIndividualData(idx)
    area_name = getAreaName(member['area_idx'])
    return render_template('%s/individual/show.html' % camp, camp=camp, member=member, area_name=area_name)

# 개인 신청 수정
@context.route('/<camp>/individual/<idx>/edit')
def edit_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))

    member = getIndividualData(idx)
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    area_list = getAreaList('cbtj') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('%s/individual/edit.html' % camp, camp=camp, campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 수정된 신청서 저장
@context.route('/<camp>/individual/<idx>/edit', methods=['POST'])
def edit_inidividual_proc(camp, idx):
    formData = getIndividualFormData()
    camp_idx = getCampIdx(camp)
    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('edit_individual', camp=camp, idx=idx))
    else:
        editIndividual(camp_idx, idx, formData)
        flash(u'신청서 수정이 완료되었습니다.')
        return redirect(url_for('show_individual', camp=camp, idx=idx))

# 신청 취소
@context.route('/<camp>/individual/<idx>/cancel')
def cancel_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))

    return render_template('%s/individual/cancel.html' % camp)

# 신청 취소 적용
@context.route('/<camp>/individual/<idx>/cancel', methods=['POST'])
def cancel_individual_proc(camp, idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('home'))

# 단체 아이디 중복체크
@context.route('/<camp>/group/check-groupid', methods=['POST'])
def check_groupid(camp):
    campidx = getCampIdx(camp)
    userid = request.form.get('groupid')
    return "%d" % checkGroupId(campidx, userid)

# 단체신청
@context.route('/<camp>/group/add')
def reg_group(camp):
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    return render_template('%s/group/add.html' % camp, camp_idx=campidx, area_list=getAreaList('cbtj'))

# 단체신청 저장
@context.route('/<camp>/group/add', methods=['POST'])
def reg_group_proc(camp):
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    groupid = request.form.get('groupid', None)

    check = checkGroupId(campidx, groupid)
    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('reg_group', camp=camp))

    else:
        formData = getGroupFormData()
        group_idx = regGroup(campidx, formData)

        session['type'] = u'단체'
        session['idx'] = group_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('show_group', camp=camp))

# 단체신청 조회
@context.route('/<camp>/group/info')
def show_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    group = getGroupData(idx)
    member_list = getMemberList(idx)
    return render_template('%s/group/show.html' % camp, group=group, area=getAreaName(group['area_idx']), member_list=member_list)

# 단체 수정
@context.route('/<camp>/group/edit')
def edit_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    group = getGroupData(idx)
    campidx = getCampIdx(camp)
    area_list = getAreaList('cbtj') # form에 들어갈 지부 목록
    return render_template('%s/group/edit.html' % camp, group=group, area_list=area_list, campidx=campidx)

# 단체 수정 저장
@context.route('/<camp>/group/edit', methods=['POST'])
def edit_group_proc(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    formData = getGroupFormData()
    editGroup(idx, formData)
    flash(u"단체 정보 수정이 완료되었습니다.")
    return redirect(url_for('show_group', camp=camp))

# 단체 취소
@context.route('/<camp>/group/cancel')
def cancel_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    return render_template('%s/group/cancel.html' % camp)

# 단체 취소 저장
@context.route('/<camp>/group/cancel', methods=['POST'])
def cancel_group_proc(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    cancel_reason = request.form.get('cancel_reason', None)
    cancelGroup(idx, cancel_reason)
    flash(u"단체 신청이 모두 취소되었습니다.")
    return redirect(url_for('home'))


# 단체 멤버 추가
@context.route('/<camp>/group/member/add')
def member_add(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('%s/individual/add.html' % camp, camp=camp, campidx=campidx,
        date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 추가 적용
@context.route('/<camp>/group/member/add', methods=['POST'])
def member_add_proc(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('member_add', camp=camp))
    else:
        regIndividual(campidx, formData, idx)
        inc_mem_num(idx)
        flash(u'멤버 추가가 완료되었습니다.')
        return redirect(url_for('show_group', camp=camp))

# 단체 멤버 수정
@context.route('/<camp>/group/member/edit/<member_idx>')
def member_edit(camp, member_idx):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    campidx = getCampIdx(camp)
    member = getIndividualData(member_idx)
    area_list = getAreaList('cbtj') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('%s/individual/edit.html' % camp, camp=camp, campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 수정 저장
@context.route('/<camp>/group/member/edit/<member_idx>', methods=['POST'])
def membet_edit_proc(camp, member_idx):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))
    idx = session['idx']
    campidx = getCampIdx(camp)
    formData = getIndividualFormData()

    date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
    date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
    td = date_of_leave - date_of_arrival
    if td.days < 0:
        flash(u'참석 기간을 잘못 선택하셨습니다.')
        return redirect(url_for('member_edit', camp=camp, member_idx=member_idx))
    else:
        editIndividual(campidx, member_idx, formData, idx)
        flash(u'신청서 수정이 완료되었습니다.')
        return redirect(url_for('show_group', camp=camp))

# 신청 취소
@context.route('/<camp>/group/member/cancel/<member_idx>')
def member_cancel(camp, member_idx):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('login', camp=camp))

    return render_template('%s/individual/cancel.html' % camp)

# 신청 취소 적용
@context.route('/<camp>/group/member/cancel/<member_idx>', methods=['POST'])
def member_cancel_proc(camp, member_idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(member_idx, cancel_reason)
    idx = session['idx']
    dec_mem_num(idx)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('show_group', camp=camp))

# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('home'))
