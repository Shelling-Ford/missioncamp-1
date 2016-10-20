# -*-coding:utf-8-*-
from flask import render_template, redirect, url_for, session, flash, Blueprint, request
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import datetime

from core.models import Member, Room, Camp, Group, Area
from core.database import db
from core.forms import GroupForm
from core.forms.cmc import RegistrationForm, GroupMemberRegForm


context = Blueprint('cmc', __name__, template_folder='templates', url_prefix='/cmc')


def check_session(logintype):
    return True if 'type' not in session or session['type'] != logintype or 'idx' not in session else False


@context.route('/')
def home():
    return render_template('cmc/home.html')


@context.route('/invitation')
def invitation():
    return render_template('cmc/invitation.html')


@context.route('/charyang')
def charyang():
    return render_template('cmc/charyang.html')


@context.route('/recommendation')
def recommendation():
    return render_template('cmc/recommendation.html')


@context.route('/room-check', methods=['GET', 'POST'])
def room_check():
    if request.method == 'POST':
        contact = '-'.join([request.form.get('hp'), request.form.get('hp2'), request.form.get('hp3')])
        name = request.form.get('name')

        try:
            member = db.session.query(Member).filter(Member.contact == contact, Member.name == name, Member.cancel_yn == 0, or_(Member.camp_idx == Camp.get_idx('cmc'), Member.camp_idx == Camp.get_idx('cbtj'))).one()
        except NoResultFound:
            return render_template('cmc/room-check-result.html', room=None, msg=u'접수된 신청 정보가 없습니다^^ 이름과 연락처를 확인해주세요', name=name)
        except MultipleResultsFound:
            return render_template('cmc/room-check-result.html', room=None, msg=u'청대, 청직 중복신청자입니다. 로비의 숙소배치팀에 문의해주세요.', name=name)

        room_idx = member.room_idx

        if room_idx is not None:
            room = Room.get(room_idx)
            return render_template('cmc/room-check-result.html', room=room, camp=member.camp.name, name=name)
        else:
            return render_template('cmc/room-check-result.html', room=None, camp=member.camp.name, msg=u'숙소가 배치되지 않았습니다^^ 로비의 숙소배치팀에 문의해주세요', name=name)

    else:
        from core.forms import RoomCheckForm
        form = RoomCheckForm()
        return render_template('cmc/room-check.html', form=form)


@context.route('/camp')
def camp():
    return redirect(url_for('.home'))


# 아이디 중복체크
@context.route('/individual/check-userid', methods=['POST'])
@context.route('/group/member/check-userid', methods=['POST'])
def check_userid():
    campidx = Camp.get_idx('cmc')
    userid = request.form.get('userid')
    return "%d" % Member.check_userid(campidx, userid)


# 개인신청 - 신청서
@context.route('/individual/add', methods=["GET", "POST"])
def reg_individual():
    form = RegistrationForm(request.form)

    if request.method == "POST":
        idx = form.insert()
        flash('신청이 완료되었습니다.')
        session['type'] = u'개인'
        session['idx'] = idx
        return redirect(url_for('.show_individual'))

    return render_template('cmc/form.html', form=form, page_header=u"개인신청", script=url_for('static', filename='cmc/js/reg-individual.js'))


# 개인 신청 수정
@context.route('/individual/edit', methods=["GET", "POST"])
def edit_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    idx = session['idx']

    form = RegistrationForm(request.form)
    if request.method == "POST":
        form.update(idx)
        flash(u'수정이 완료되었습니다')
        return redirect(url_for('.show_individual'))

    member = Member.get(idx)
    form.set_member_data(member)
    return render_template('cmc/form.html', form=form, page_header=u"개인 신청서 수정", script=url_for('static', filename='cmc/js/reg-individual-edit.js'), editmode=True)


# 신청조회 - 로그인 폼
@context.route('/check')
def login():
    return render_template('cmc/check.html')


@context.route('/check', methods=['POST'])
def login_proc():
    logintype = request.form.get('logintype', None)
    if logintype == '' or logintype is None:
        flash(u'신청 구분을 선택해주세요')
        return redirect(url_for('.login'))

    userid = request.form.get('userid', None)
    if userid == '' or userid is None:
        flash(u'아이디를 입력해주세요')
        return redirect(url_for('.login'))

    pwd = request.form.get('pwd', None)
    if pwd == '' or pwd is None:
        flash(u'비밀번호를 입력해 주세요')
        return redirect(url_for('.login'))

    campidx = Camp.get_idx('cmc')
    if logintype == u'개인':
        if Member.login_check(campidx, userid, pwd):
            idx = Member.get_idx(campidx, userid)
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('.show_individual'))
        else:
            flash(u'아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login'))
    elif logintype == u'단체':
        if Group.login_check(campidx, userid, pwd):
            idx = Group.get_idx(campidx, userid)
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
    member = Member.get(idx)
    membership_data = member.get_membership_data()
    area_name = Area.get_name(member.area_idx)
    return render_template('cmc/individual/show.html', camp='cmc', member=member, membership_data=membership_data, area_name=area_name)


# 신청 취소
@context.route('/individual/cancel', methods=["GET", "POST"])
def cancel_individual():
    if check_session(u'개인'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    if request.method == "POST":
        cancel_reason = request.form.get('cancel_reason', None)
        idx = session['idx']
        member = db.session.query(Member).filter(Member.idx == idx).one()
        member.cancel_yn = 1
        member.cancel_reason = cancel_reason
        member.canceldate = datetime.datetime.today()
        db.session.commit()

        flash(u'신청이 취소되었습니다')
        return redirect(url_for('.home'))
    return render_template('cmc/individual/cancel.html')


# 단체 아이디 중복체크
@context.route('/group/check-groupid', methods=['POST'])
def check_groupid():
    campidx = Camp.get_idx('cmc')
    userid = request.form.get('groupid')
    return "%d" % Group.check_groupid(campidx, userid)


# 단체신청
@context.route('/group/add', methods=["GET", "POST"])
def reg_group():
    form = GroupForm(request.form)

    if request.method == "POST":
        group_idx = form.insert(Camp.get_idx("cmc"))

        session['type'] = u'단체'
        session['idx'] = group_idx

        flash(u'신청이 완료되었습니다.')
        return redirect(url_for('.show_group'))

    return render_template('cmc/form.html', form=form, page_header=u"단체신청", script=url_for('static', filename='common/js/reg-group.js'))


# 단체신청 조회
@context.route('/group/info')
def show_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    idx = session['idx']
    group = Group.get(idx)
    member_list = db.session.query(Member).filter(Member.group_idx == idx, Member.cancel_yn == 0).all()
    return render_template('cmc/group/show.html', group=group, area=Area.get_name(group.area_idx), member_list=member_list)


# 단체 수정
@context.route('/group/edit', methods=["GET", "POST"])
def edit_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))
    
    idx = session['idx']
    form = GroupForm(request.form)

    if request.method == "POST":
        form.update(Camp.get_idx('cmc'), idx)
        flash(u"단체 정보 수정이 완료되었습니다.")
        return redirect(url_for('.show_group'))

    group = Group.get(idx)
    form.set_group_data(group)
    return render_template('cmc/form.html', form=form, page_header=u"단체신청 수정", script=url_for('static', filename='common/js/reg-group-edit.js'), editmode=True)


# 단체 취소
@context.route('/group/cancel', methods=["GET", "POST"])
def cancel_group():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    if request.method == "POST":
        idx = session['idx']
        cancel_reason = request.form.get('cancel_reason', None)
        group = Group.get(idx)
        group.cancel_yn = 1
        group.cancel_reason = cancel_reason
        group.canceldate = datetime.datetime.today()

        member_list = db.session.query(Member).filter(Member.group_idx == idx).all()

        for member in member_list:
            member.cancel_yn = 1
            member.cancel_reason = "단체취소: " + cancel_reason
            member.canceldate = datetime.datetime.today()

        db.session.commit()
        flash(u"단체 신청이 모두 취소되었습니다.")
        return redirect(url_for('.home'))

    return render_template('cmc/group/cancel.html')


# 단체 멤버 추가
@context.route('/group/member/add', methods=["GET", "POST"])
def member_add():
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    form = GroupMemberRegForm(request.form)
    
    idx = session['idx']
    form.group_idx.data = idx
    group = Group.get(idx)

    if request.method == "POST":
        form.insert(group.idx, group.area_idx)
        group.mem_num += 1
        db.session.commit()
        flash(u"멤버가 추가되었습니다.")
        return redirect(url_for(".show_group"))

    return render_template('cmc/form.html', form=form, page_header="멤버 추가", script=url_for('static', filename='cmc/js/reg-individual.js'))


# 단체 멤버 수정
@context.route('/group/member/edit/<member_idx>', methods=["GET", "POST"])
def member_edit(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    form = GroupMemberRegForm(request.form)
    idx = session['idx']
    form.group_idx.data = idx

    if request.method == "POST":
        form.update(member_idx)
        flash(u"성공적으로 수정되었습니다.")
        return redirect(url_for(".show_group"))

    member = Member.get(member_idx)
    form.set_member_data(member)
    return render_template('cmc/form.html', form=form, page_header="멤버 수정", script=url_for('static', filename='cmc/js/reg-individual-edit.js'))


# 신청 취소
@context.route('/group/member/cancel/<member_idx>', methods=["GET", "POST"])
def member_cancel(member_idx):
    if check_session(u'단체'):
        flash(u'로그아웃 되었습니다. 다시 로그인하세요')
        return redirect(url_for('.login'))

    if request.method == "POST":
        cancel_reason = request.form.get('cancel_reason', None)
        member = Member.get(member_idx)
        member.cancel_yn = 1
        member.cancel_reason = cancel_reason
        member.canceldate = datetime.datetime.today()
        db.session.commit()

        idx = session['idx']
        group = Group.get(idx)
        group.mem_num -= 1
        if group.mem_num < 0:
            group.mem_num = 0
        db.session.commit()

        flash(u'신청이 취소되었습니다')
        return redirect(url_for('.show_group'))
    return render_template('cmc/individual/cancel.html')


# 로그아웃
@context.route('/logout')
def logout():
    session.clear()
    flash(u'정상적으로 로그아웃 되었습니다.')
    return redirect(url_for('.home'))
