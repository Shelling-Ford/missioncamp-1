# -*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from jinja2 import TemplateNotFound
from core.functions import *
from core.functions.cbtj import *
from core.forms import GroupForm
from core.forms.cbtj import RegistrationForm, GroupMemberRegForm
from core.models import Member, Group, Area, Camp
from core.database import db
from missioncamp.functions.cbtj import *

context = Blueprint('cbtj', __name__, template_folder='templates', url_prefix='/cbtj')


# camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
def check_campcode(camp):
    if camp != 'cbtj' and camp != 'cbtj2':
        print u'잘못된 접근: 캠프코드가 cbtj 또는 cbtj2가 아닙니다.'
        raise BaseException


def check_session(camp, logintype, idx=None):
    return True if not 'type' in session or session['type'] != logintype or not 'idx' in session else False


@context.route('/')
def home():
    return render_template('cbtj/home.html')


@context.route('/<page>')
def page(page):
    try:
        return render_template('cbtj/%s.html' % page)
    except TemplateNotFound:
        return render_template('cbtj/404.html')


@context.route('/room-check', methods=['GET', 'POST'])
def room_check():
    if request.method == 'POST':
        contact = '-'.join([request.form.get('hp'), request.form.get('hp2'), request.form.get('hp3')])
        name = request.form.get('name')

        from core.models import Member, Room
        from core.database import db
        from core.models import Camp
        from sqlalchemy import or_
        try:
            member = db.db_session.query(Member).filter(Member.contact == contact, Member.name == name, Member.cancel_yn == 0, or_(Member.camp_idx == Camp.get_idx('cbtj'))).one()
        except NoResultFound:
            return render_template('cbtj/room-check-result.html', room=None, msg=u'접수된 신청 정보가 없습니다^^ 이름과 연락처를 확인해주세요', name=name)

        room_idx = member.room_idx

        if room_idx is not None:
            room = Room.get(room_idx)
            return render_template('cbtj/room-check-result.html', room=room, name=name)
        else:
            return render_template('cbtj/room-check-result.html', room=None, msg=u'숙소가 배치되지 않았습니다^^ 로비의 숙소배치팀에 문의해주세요', name=name)
    else:
        from core.forms import RoomCheckForm
        form = RoomCheckForm()
        return render_template('cbtj/room-check.html', form=form)


@context.route('/<camp>/')
def camp(camp):
    return render_template('cbtj/%s/home.html' % camp)


# 아이디 중복체크
@context.route('/<camp>/individual/check-userid', methods=['POST'])
@context.route('/<camp>/group/member/check-userid', methods=['POST'])
def check_userid(camp):
    campidx = getCampIdx(camp)
    userid = request.form.get('userid')
    return "%d" % checkUserId(campidx, userid)


# 개인신청 - 신청서
@context.route('/<camp>/individual/add', methods=["GET", "POST"])
def reg_individual(camp):
    check_campcode(camp)  # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    form = RegistrationForm(request.form)

    if request.method == "POST":
        idx = form.insert()
        flash('신청이 완료되었습니다.')
        session['type'] = u'개인'
        session['idx'] = idx
        return redirect(url_for('.show_individual', camp=camp, idx=idx))

    return render_template('cbtj/form.html', form=form, page_header=u"개인신청", script=url_for('static', filename='cbtj/js/reg-individual.js'))


# 신청조회 - 로그인 폼
@context.route('/<camp>/check')
def login(camp):
    return render_template('cbtj/%s/check.html' % camp)


@context.route('/<camp>/check', methods=['POST'])
def login_proc(camp):
    logintype = request.form.get('logintype', None)
    if logintype == '' or logintype is None:
        flash(u'신청 구분을 선택해주세요')
        return redirect(url_for('.login', camp=camp))

    userid = request.form.get('userid', None)
    if userid == '' or userid is None:
        flash(u'아이디를 입력해주세요')
        return redirect(url_for('.login', camp=camp))

    pwd = request.form.get('pwd', None)
    if pwd == '' or pwd is None:
        flash(u'비밀번호를 입력해 주세요')
        return redirect(url_for('.login', camp=camp))

    campidx = getCampIdx(camp)
    if logintype == u'개인':
        if loginCheckUserid(campidx, userid, pwd):
            idx = getUserIdx(campidx, userid)
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('.show_individual', camp=camp, idx=idx))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login', camp=camp))
    elif logintype == u'단체':
        print loginCheckGroupid(campidx, userid, pwd)
        if loginCheckGroupid(campidx, userid, pwd):
            idx = getGroupIdx(campidx, userid)
            session['type'] = u'단체'
            session['idx'] = idx
            return redirect(url_for('.show_group', camp=camp))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login', camp=camp))
    else:
        flash('신청구분이 잘못되었습니다. 관리자에게 문의해주세요(070-8787-8870)')
        return redirect(url_for('.login', camp=camp))


# 개인신청 조회
@context.route('/<camp>/individual/<idx>')
def show_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    member = getIndividualData(idx)
    area_name = getAreaName(member['area_idx'])
    return render_template('cbtj/%s/individual/show.html' % camp, camp=camp, member=member, area_name=area_name)


# 개인 신청 수정
@context.route('/<camp>/individual/<idx>/edit', methods=["GET", "POST"])
def edit_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    idx = session['idx']

    form = RegistrationForm(request.form)
    if request.method == "POST":
        form.update(idx)
        flash(u'수정이 완료되었습니다')
        return redirect(url_for('.show_individual', camp=camp, idx=idx))

    member = Member.get(idx)
    form.set_member_data(member)
    return render_template('cbtj/form.html', form=form, page_header=u"개인 신청서 수정", script=url_for('static', filename='cbtj/js/reg-individual-edit.js'), editmode=True)


# 신청 취소
@context.route('/<camp>/individual/<idx>/cancel')
def cancel_individual(camp, idx):
    if check_session(camp, u'개인', idx):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    return render_template('cbtj/%s/individual/cancel.html' % camp)

# 신청 취소 적용
@context.route('/<camp>/individual/<idx>/cancel', methods=['POST'])
def cancel_individual_proc(camp, idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(idx, cancel_reason)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.home'))

# 단체 아이디 중복체크
@context.route('/<camp>/group/check-groupid', methods=['POST'])
def check_groupid(camp):
    campidx = getCampIdx(camp)
    userid = request.form.get('groupid')
    return "%d" % checkGroupId(campidx, userid)

# 단체신청
@context.route('/<camp>/group/add', methods=["GET", "POST"])
def reg_group(camp):
    check_campcode(camp) # camp code  가 cbtj 또는 cbtj2가 아닐 경우 오류 페이지로 리다이렉션
    form = GroupForm(request.form)
    form.set_camp(camp)

    if request.method == "POST":
        group_idx = form.insert(Camp.get_idx(camp))

        session['type'] = u'단체'
        session['idx'] = group_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_group', camp=camp))

    return render_template('cbtj/form.html', form=form, page_header=u"단체신청", script=url_for('static', filename='common/js/reg-group.js'))


# 단체신청 조회
@context.route('/<camp>/group/info')
def show_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))
    idx = session['idx']
    group = getGroupData(idx)
    member_list = getMemberList(idx)
    return render_template('cbtj/%s/group/show.html' % camp, group=group, area=getAreaName(group['area_idx']), member_list=member_list)

# 단체 수정
@context.route('/<camp>/group/edit', methods=["GET", "POST"])
def edit_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    idx = session['idx']
    form = GroupForm(request.form)
    form.set_camp(camp)

    if request.method == "POST":
        form.update(Camp.get_idx(camp), idx)
        flash(u"단체 정보 수정이 완료되었습니다.")
        return redirect(url_for('.show_group', camp=camp))

    group = Group.get(idx)
    form.set_group_data(group)
    return render_template('cbtj/form.html', form=form, page_header=u"단체신청 수정", script=url_for('static', filename='common/js/reg-group-edit.js'), editmode=True)


# 단체 취소
@context.route('/<camp>/group/cancel')
def cancel_group(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))
    return render_template(cbtj/'%s/group/cancel.html' % camp)

# 단체 취소 저장
@context.route('/<camp>/group/cancel', methods=['POST'])
def cancel_group_proc(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))
    idx = session['idx']
    cancel_reason = request.form.get('cancel_reason', None)
    cancelGroup(idx, cancel_reason)
    flash(u"단체 신청이 모두 취소되었습니다.")
    return redirect(url_for('.home'))


# 단체 멤버 추가
@context.route('/<camp>/group/member/add', methods=["GET", "POST"])
def member_add(camp):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    form = GroupMemberRegForm(request.form)

    idx = session['idx']
    form.group_idx.data = idx
    group = Group.get(idx)

    if request.method == "POST":
        form.insert(group.idx, group.area_idx)
        group.mem_num += 1
        db.session.commit()
        flash(u"멤버가 추가되었습니다.")
        return redirect(url_for(".show_group", camp=camp))

    return render_template('cbtj/form.html', form=form, page_header="멤버 추가", script=url_for('static', filename='cbtj/js/reg-individual.js'))


# 단체 멤버 수정
@context.route('/<camp>/group/member/edit/<member_idx>', methods=["GET", "POST"])
def member_edit(camp, member_idx):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))
    
    form = GroupMemberRegForm(request.form)
    idx = session['idx']
    form.group_idx.data = idx

    if request.method == "POST":
        form.update(member_idx)
        flash(u"성공적으로 수정되었습니다.")
        return redirect(url_for(".show_group", camp=camp))

    member = Member.get(member_idx)
    form.set_member_data(member)
    return render_template('cbtj/form.html', form=form, page_header="멤버 수정", script=url_for('static', filename='cbtj/js/reg-individual-edit.js'))


# 신청 취소
@context.route('/<camp>/group/member/cancel/<member_idx>')
def member_cancel(camp, member_idx):
    if check_session(camp, u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login', camp=camp))

    return render_template('cbtj/%s/individual/cancel.html' % camp)

# 신청 취소 적용
@context.route('/<camp>/group/member/cancel/<member_idx>', methods=['POST'])
def member_cancel_proc(camp, member_idx):
    cancel_reason = request.form.get('cancel_reason', None)
    cancelIndividual(member_idx, cancel_reason)
    idx = session['idx']
    dec_mem_num(idx)
    flash(u'신청이 취소되었습니다')
    return redirect(url_for('.show_group', camp=camp))

# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('.home'))
