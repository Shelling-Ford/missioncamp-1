#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, session, flash, Blueprint
from core.functions import *
from core.functions.ws import *

context = Blueprint('ws', __name__, template_folder='templates', url_prefix='/ws')

def check_session(logintype):
    return True if not 'type' in session or session['type'] != logintype or not 'idx' in session else False

@context.route('/')
def home():
    return render_template('ws/home.html')

@context.route('/invitation')
def invitation():
    return render_template('ws/invitation.html')

@context.route('/recommendation')
def recommendation():
    return render_template('ws/recommendation.html')



@context.route('/room-check', methods=['GET', 'POST'])
def room_check():
    if request.method == 'POST':
        contact = '-'.join([request.form.get('hp'), request.form.get('hp2'), request.form.get('hp3')])
        name = request.form.get('name')
        logintype = request.form.get('logintype')

        from core.models import Member, Room, Group
        from core.database import db
        from core.models import Camp
        from sqlalchemy import or_
        from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

        if logintype == u'개인':
            try:
                member = db.db_session.query(Member).filter(Member.contact == contact, Member.name == name, Member.cancel_yn == 0, or_(Member.camp_idx == Camp.get_idx('ws'))).one()
                member_list = [member]
                group_name = None
            except NoResultFound:
                return render_template('ws/room-check-result.html', msg=u'접수된 신청 정보가 없습니다^^ 이름과 연락처를 확인해주세요', name=name)
            except MultipleResultsFound:
                return render_template('ws/room-check-result.html', msg=u'중복신청자입니다. 로비의 숙소배치팀에 문의해주세요.', name=name)
        elif logintype == u'단체':
            try:
                group = db.db_session.query(Group).filter(Group.leadercontact == contact, Group.leadername == name, Group.cancel_yn == 0, or_(Group.camp_idx == Camp.get_idx('ws'), Group.camp_idx == Camp.get_idx('cbtj2'))).one()
                member_list = Member.get_list(group.camp_idx, group_idx=group.idx)
                group_name = group.name
            except NoResultFound:
                return render_template('ws/room-check-result.html', msg=u'접수된 신청 정보가 없습니다^^ 이름과 연락처를 확인해주세요', name=name)
            except MultipleResultsFound:
                return render_template('ws/room-check-result.html', msg=u'중복신청자입니다. 로비의 숙소배치팀에 문의해주세요.', name=name)
        else:
            pass

        return render_template('ws/room-check-result.html', member_list=member_list, group_name=group_name)

    else:
        from core.forms import RoomCheckForm
        form = RoomCheckForm()
        return render_template('ws/room-check.html', form=form)



@context.route('/camp')
def camp():
    return redirect(url_for('home'))

# 아이디 중복체크
@context.route('/individual/check-userid', methods=['POST'])
@context.route('/group/member/check-userid', methods=['POST'])
def check_userid():
    campidx = getCampIdx('ws')
    userid = request.form.get('userid')
    return "%d" % checkUserId(campidx, userid)

# 개인신청 - 신청서
@context.route('/individual/add')
def reg_individual():
    campidx = getCampIdx('ws')
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('ws/individual/add.html', camp='ws', campidx=campidx,
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 개인신청 - 신청서를 데이터베이스에 저장
@context.route('/individual/add', methods=['POST'])
def reg_individual_proc():
    campidx = getCampIdx('ws')
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
    return render_template('ws/check.html')

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

    campidx = getCampIdx('ws')
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
    return render_template('ws/individual/show.html', camp='ws', member=member, area_name=area_name)

# 개인 신청 수정
@context.route('/individual/edit')
def edit_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    idx = session['idx']
    member = getIndividualData(idx)
    campidx = getCampIdx('ws')
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('ws/individual/edit.html', camp='ws', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=False)

# 수정된 신청서 저장
@context.route('/individual/edit', methods=['POST'])
def edit_inidividual_proc():
    formData = getIndividualFormData()
    camp_idx = getCampIdx('ws')

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

    return render_template('ws/individual/cancel.html')

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
    campidx = getCampIdx('ws')
    userid = request.form.get('groupid')
    return "%d" % checkGroupId(campidx, userid)

# 단체신청
@context.route('/group/add')
def reg_group():
    campidx = getCampIdx('ws')
    return render_template('ws/group/add.html', camp_idx=campidx, area_list=getAreaList('ws'))

# 단체신청 저장
@context.route('/group/add', methods=['POST'])
def reg_group_proc():
    campidx = getCampIdx('ws')
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
    return render_template('ws/group/show.html', group=group, area=getAreaName(group['area_idx']), member_list=member_list)

# 단체 수정
@context.route('/group/edit')
def edit_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    group = getGroupData(idx)
    campidx = getCampIdx('ws')
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    return render_template('ws/group/edit.html', group=group, area_list=area_list, campidx=campidx)

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
    return render_template('ws/group/cancel.html')

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
    campidx = getCampIdx('ws')
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('ws/individual/add.html', camp='ws', campidx=campidx,
        date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 추가 적용
@context.route('/group/member/add', methods=['POST'])
def member_add_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('ws')
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
    campidx = getCampIdx('ws')
    member = getIndividualData(member_idx)
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    group = getGroupData(idx)
    return render_template('ws/individual/edit.html', camp='ws', campidx=campidx, member=member, membership=member['membership'],
        area_list=area_list, date_select_list=date_select_list, group_yn=True, group=group)

# 단체 멤버 수정 저장
@context.route('/group/member/edit/<member_idx>', methods=['POST'])
def membet_edit_proc(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    campidx = getCampIdx('ws')
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

    return render_template('ws/individual/cancel.html')

# 신청 취소 적용
@context.route('/group/member/cancel/<member_idx>', methods=['POST'])
def member_cancel_proc(member_idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(member_idx, cancel_reason)
    idx = session['idx']
    dec_mem_num(idx)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.show_group'))

# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('.home'))