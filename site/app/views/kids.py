#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, session, flash, Blueprint, request
#from core.functions import *
#from core.functions.kids import *
from core.functions import getIndividualFormData, getGroupFormData
from core.functions.kids import getMembershipDataList
from core.models import Camp, Promotion, Member, Group
from core.forms import GroupForm
from core.forms.kids import RegistrationForm, GroupMemberRegForm

context = Blueprint('kids', __name__, template_folder='templates', url_prefix='/kids')

def check_session(logintype):
    return True if not 'type' in session or session['type'] != logintype or not 'idx' in session else False

@context.route('/')
def home():
    return render_template('kids/home.html')

# 아이디 중복체크
@context.route('/individual/check-userid', methods=['POST'])
@context.route('/group/member/check-userid', methods=['POST'])
def check_userid():
    campidx = Camp.get_idx('kids')
    userid = request.form.get('userid')
    return "%d" % Member.check_userid(campidx, userid)

# 개인신청 - 신청서
@context.route('/individual/add')
def reg_individual():
    form = RegistrationForm()
    return render_template('kids/form.html', form=form, page_header=u"개인신청", script=url_for('static', filename='kids/js/reg-individual.js'))

# 개인신청 - 신청서를 데이터베이스에 저장
@context.route('/individual/add', methods=['POST'])
def reg_individual_proc():
    campidx = Camp.get_idx('kids')
    userid = request.form.get('userid', None)

    check = Member.check_userid(campidx, userid)
    formData = getIndividualFormData()

    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('.reg_individual')+'#content')
    else:
        member_idx = Member.insert(campidx, formData, None, getMembershipDataList(campidx, formData))
        session['type'] = u'개인'
        session['idx'] = member_idx
        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_individual')+'#content')

# 신청조회 - 로그인 폼
@context.route('/check')
def login():
    return render_template('kids/check.html')

@context.route('/check', methods=['POST'])
def login_proc():
    logintype = request.form.get('logintype', None)
    if logintype == '' or logintype == None:
        flash(u'신청 구분을 선택해주세요')
        return redirect(url_for('.login')+'#content')

    userid = request.form.get('userid', None)
    if userid == '' or userid == None:
        flash(u'아이디를 입력해주세요')
        return redirect(url_for('.login')+'#content')

    pwd = request.form.get('pwd', None)
    if pwd == '' or pwd == None:
        flash(u'비밀번호를 입력해 주세요')
        return redirect(url_for('.login')+'#content')

    campidx = Camp.get_idx('kids')
    if logintype == u'개인':
        if Member.login_check(campidx, userid, pwd):
            idx = Member.get_idx(campidx, userid)
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('.show_individual')+'#content')
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login')+'#content')
    elif logintype == u'단체':
        if Group.login_check(campidx, userid, pwd):
            idx = Group.get_idx(campidx,userid)
            session['type'] = u'단체'
            session['idx'] = idx
            return redirect(url_for('.show_group')+'#content')
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login')+'#content')
    else:
        flash('신청구분이 잘못되었습니다. 관리자에게 문의해주세요(070-8787-8870)')
        return redirect(url_for('.login')+'#content')

# 개인신청 조회
@context.route('/individual/info')
def show_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')

    idx = session['idx']
    member = Member.get(idx)
    return render_template('kids/individual/show.html', member=member)

# 개인 신청 수정
@context.route('/individual/edit')
def edit_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')

    idx = session['idx']
    member = Member.get(idx)
    form = RegistrationForm()
    form.set_member_data(member)
    return render_template('kids/form.html', form=form, page_header=u"개인신청 수정", script=url_for('static', filename='kids/js/reg-individual-edit.js'), editmode=True)


# 수정된 신청서 저장
@context.route('/individual/edit', methods=['POST'])
def edit_inidividual_proc():
    formData = getIndividualFormData()
    camp_idx = Camp.get_idx('kids')
    idx = session['idx']
    Member.update(idx, camp_idx, formData=formData, membership_data_list=getMembershipDataList(camp_idx, formData))
    flash(u'신청서 수정이 완료되었습니다.')
    return redirect(url_for('.show_individual', idx=idx)+'#content')

# 신청 취소
@context.route('/individual/cancel')
def cancel_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')

    return render_template('kids/individual/cancel.html')

# 신청 취소 적용
@context.route('/individual/cancel', methods=['POST'])
def cancel_individual_proc():
    cancel_reason = request.form.get('cancel_reason', None)
    idx = session['idx']
    Member.cancle(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.home')+'#content')

# 단체 아이디 중복체크
@context.route('/group/check-groupid', methods=['POST'])
def check_groupid():
    campidx = Camp.get_idx('kids')
    groupid = request.form.get('groupid')
    return "%d" % Group.check_groupid(campidx, groupid)

# 단체신청
@context.route('/group/add')
def reg_group():
    form = GroupForm()
    return render_template('kids/form.html', form=form, page_header=u"단체신청", script=url_for('static', filename='kids/js/reg-group.js'))

# 단체신청 저장
@context.route('/group/add', methods=['POST'])
def reg_group_proc():
    campidx = Camp.get_idx('kids')
    groupid = request.form.get('groupid', None)

    check = Group.check_groupid(campidx, groupid)
    if check > 0:
        # 아이디 중복 관련 Exception을 발생시킴
        flash(u'중복된 아이디입니다. 아이디를 다시 확인해주세요.')
        return redirect(url_for('.reg_group')+'#content')

    else:
        formData = getGroupFormData()
        group_idx = Group.insert(campidx, formData)

        session['type'] = u'단체'
        session['idx'] = group_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_group')+'#content')

# 단체신청 조회
@context.route('/group/info')
def show_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    camp_idx = Camp.get_idx('kids')
    group = Group.get(idx)
    member_list = Member.get_list(camp_idx, group_idx=idx)
    return render_template('kids/group/show.html', group=group, member_list=member_list)

# 단체 수정
@context.route('/group/edit')
def edit_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    group = Group.get(idx)
    form = GroupForm()
    form.set_group_data(group)
    return render_template('kids/form.html', form=form, page_header=u"단체신청 수정", script=url_for('static', filename='kids/js/reg-group-edit.js'), editmode=True)

# 단체 수정 저장
@context.route('/group/edit', methods=['POST'])
def edit_group_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    formData = getGroupFormData()
    Group.update(idx, formData)
    flash(u"단체 정보 수정이 완료되었습니다.")
    return redirect(url_for('.show_group')+'#content')

# 단체 취소
@context.route('/group/cancel')
def cancel_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    return render_template('kids/group/cancel.html')

# 단체 취소 저장
@context.route('/group/cancel', methods=['POST'])
def cancel_group_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    cancel_reason = request.form.get('cancel_reason', None)
    Group.cancel(idx, cancel_reason)
    flash(u"단체 신청이 모두 취소되었습니다.")
    return redirect(url_for('.home')+'#content')


# 단체 멤버 추가
@context.route('/group/member/add')
def member_add():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    group = Group.get(idx)
    form = GroupMemberRegForm()
    form.set_group_idx(idx)
    form.set_area_idx(group.area_idx)
    return render_template('kids/form.html', form=form, page_header="멤버 추가", script=url_for('static', filename='kids/js/reg-individual.js'))

# 단체 멤버 추가 적용
@context.route('/group/member/add', methods=['POST'])
def member_add_proc():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    campidx = Camp.get_idx('kids')
    formData = getIndividualFormData()
    member_idx = Member.insert(campidx, formData, idx, getMembershipDataList(campidx, formData))
    Group.inc_mem_num(idx)
    flash(u'멤버 추가가 완료되었습니다.')
    return redirect(url_for('.show_group')+'#content')

# 단체 멤버 수정
@context.route('/group/member/edit/<member_idx>')
def member_edit(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    form = GroupMemberRegForm()
    group = Group.get(idx)
    member = Member.get(member_idx)
    form.set_member_data(member)
    form.set_area_idx(group.area_idx)
    return render_template('kids/form.html', form=form, page_header="멤버 수정", script=url_for('static', filename='kids/js/reg-individual-edit.js'), editmode=True)

# 단체 멤버 수정 저장
@context.route('/group/member/edit/<member_idx>', methods=['POST'])
def membet_edit_proc(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')
    idx = session['idx']
    camp_idx = Camp.get_idx('kids')
    formData = getIndividualFormData()
    Member.update(member_idx, camp_idx, formData=formData, membership_data_list=getMembershipDataList(camp_idx, formData))
    flash(u'신청서 수정이 완료되었습니다.')
    return redirect(url_for('.show_group')+'#content')

# 신청 취소
@context.route('/group/member/cancel/<member_idx>')
def member_cancel(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login')+'#content')

    return render_template('kids/individual/cancel.html')

# 신청 취소 적용
@context.route('/group/member/cancel/<member_idx>', methods=['POST'])
def member_cancel_proc(member_idx):
    cancel_reason = request.form.get('cancel_reason', None)
    Member.cancel(member_idx, cancel_reason)
    idx = session['idx']
    Group.dec_mem_num(idx)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.show_group')+'#content')

@context.route('/promotion', methods=['POST'])
def save_promotion_info():
    camp_idx = Camp.get_idx('kids')
    church_name = request.form.get('church_name', None)
    name = request.form.get('name', None)
    address = request.form.get('address', None)
    contact = request.form.get('contact', None)
    memo = request.form.get('memo', None)
    next_url = request.form.get('next', None)

    Promotion.insert(camp_idx, church_name, name, address, contact, memo)
    flash(u'홍보물 신청이 완료되었습니다')
    return redirect(url_for('.home')+'#content')

# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('.home')+'#content')
