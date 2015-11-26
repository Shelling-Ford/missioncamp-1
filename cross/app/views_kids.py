#-*-coding:utf-8-*-
from flask import Blueprint, render_template, request

from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from core.models import Camp, Member, Group

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
