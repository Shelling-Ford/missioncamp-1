#-*-coding:utf-8-*-
from flask import Blueprint, render_template, request, redirect, url_for

from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from core.models import Camp, Member, Group, Payment, Area, Room

from functions import get_basic_stat

# Blueprint 초기화
kids = Blueprint('kids', __name__, template_folder='templates', url_prefix='/kids')

master_permission = Permission(RoleNeed('master'))
hq_permission = Permission(RoleNeed('hq'))
branch_permission = Permission(RoleNeed('branch'))
kids_permission = Permission(RoleNeed('kids'))

# 메인 통계
@kids.route('/')
@login_required
@branch_permission.require(http_exception=403)
def home():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))
    camp_idx = Camp.get_idx('kids', year, term)
    stat = get_basic_stat(camp_idx)
    return render_template('kids/home.html', stat=stat)

# 신청자 목록
@kids.route('/list')
@login_required
@branch_permission.require(http_exception=403)
def member_list():
    camp_idx = Camp.get_idx('kids')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)
    member_name = request.args.get('name', None)
    group_idx = request.args.get('group_idx', None)

    #if current_user.role == 'branch' and current_user.area_idx != area_idx:
    #    flash(u'지부 신청자 명단만 열람 가능합니다.')
    #    area_idx = current_user.area_idx

    member_list = Member.get_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name, group_idx=group_idx)
    group = Group.get(group_idx) if group_idx is not None else None
    count = Member.count(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name, group_idx=group_idx)
    return render_template('kids/list.html', members=member_list, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name, group=group, loop=range(count))


# 신청자 상세
@kids.route('/member')
@login_required
@branch_permission.require(http_exception=403)
def member():
    camp_idx = Camp.get_idx('kids')

    member_idx = request.args.get('member_idx', 0)

    if member_idx != 0:
        member = Member.get(member_idx)
        room_list = Room.get_list()
        area_list = Area.get_list('kids')
        group_list = Group.get_list(camp_idx)

    return render_template('kids/member.html', member=member, rooms=room_list, area_list=area_list, group_list=group_list)

# 입금 정보 입력
@kids.route('/pay', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@kids_permission.require(http_exception=403)
def pay():
    member_idx = request.args.get('member_idx', 0)
    amount = request.form.get('amount')
    complete = request.form.get('complete')
    claim = request.form.get('claim')
    paydate = request.form.get('paydate')
    staff_name = request.form.get('staff_name')

    Payment.save(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)
    return redirect(url_for('.member_list'))

# 입금 정보 삭제
@kids.route('/delpay')
@login_required
@hq_permission.require(http_exception=403)
@kids_permission.require(http_exception=403)
def delpay():
    member_idx = request.args.get('member_idx', 0)
    Payment.delete(member_idx)
    return redirect(url_for('.member_list'))

# 숙소 정보 입력
@kids.route('/room_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@kids_permission.require(http_exception=403)
def room_setting():
    member_idx = request.form.get('member_idx', 0)
    room_idx = request.form.get('idx', 0)
    Member.update(member_idx=member_idx, room_idx=room_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 지부 변경
@kids.route('/area_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@kids_permission.require(http_exception=403)
def area_setting():
    member_idx = request.form.get('member_idx', 0)
    area_idx = request.form.get('area_idx', 0)
    Member.update(member_idx=member_idx, area_idx=area_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 단체 변경
@kids.route('/group_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@kids_permission.require(http_exception=403)
def group_setting():
    member_idx = request.form.get('member_idx', 0)
    group_idx = request.form.get('group_idx', 0)
    Member.update(member_idx=member_idx, group_idx=group_idx)
    return redirect(url_for('.member', member_idx=member_idx))
