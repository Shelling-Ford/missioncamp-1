#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.functions import *
from core.functions.youth import *
from core.models import Promotion, Member, Camp, Group, Area, Room
from core.forms.youth import RegistrationForm
from functions import *
import functions_mongo as mongo
import xlsxwriter

# Blueprint 초기화
youth = Blueprint('youth', __name__, template_folder='templates', url_prefix='/youth')

master_permission = Permission(RoleNeed('master'))
hq_permission = Permission(RoleNeed('hq'))
branch_permission = Permission(RoleNeed('branch'))
youth_permission = Permission(RoleNeed('youth'))

# 메인 통계
@youth.route('/')
@login_required
@branch_permission.require(http_exception=403)
def home():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = Camp.get_idx('youth')
    else:
        camp_idx = Camp.get_idx('youth', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('youth/home.html', stat=stat)

# 신청자 목록
@youth.route('/list')
@login_required
@branch_permission.require(http_exception=403)
def member_list():
    camp_idx = Camp.get_idx('youth')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)
    member_name = request.args.get('name', None)
    group_idx = request.args.get('group_idx', None)

    member_list = Member.get_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx, name=member_name, group_idx=group_idx)
    return render_template('youth/list.html', members=member_list)

# 홍보물 신청 목록
@youth.route('/promotion-list')
@login_required
@branch_permission.require(http_exception=403)
def promotion_list():
    camp_idx = Camp.get_idx('youth')
    promotion_list = Promotion.get_list(camp_idx)
    return render_template('youth/promotion_list.html', promotions=promotion_list)

# 신청자 상세
@youth.route('/member')
@login_required
@branch_permission.require(http_exception=403)
def member():
    camp_idx = Camp.get_idx('youth')

    member_idx = request.args.get('member_idx', 0)

    if member_idx != 0:
        member = Member.get(member_idx)
        room_list = Room.get_list()
        area_list = Area.get_list('youth')
        group_list = Group.get_list(camp_idx)

    return render_template('youth/member.html', member=member, rooms=room_list, area_list=area_list, group_list=group_list)


# 개인 신청 수정
@youth.route('/member-edit')
@login_required
@branch_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def member_edit():
    idx = request.args.get('member_idx', 0)
    session['idx'] = idx
    member = Member.get(idx)
    form = RegistrationForm()
    form.set_member_data(member)

    return render_template('youth/form.html', form=form)

# 입금 정보 입력
@youth.route('/pay', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def pay():
    member_idx = request.args.get('member_idx', 0)
    amount = request.form.get('amount')
    complete = request.form.get('complete')
    claim = request.form.get('claim')
    paydate = request.form.get('paydate')
    staff_name = request.form.get('staff_name')

    save_payment(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)
    return redirect(url_for('.member_list'))

# 입금 정보 삭제
@youth.route('/delpay')
@login_required
@hq_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def delpay():
    member_idx = request.args.get('member_idx', 0)
    delete_payment(member_idx)
    return redirect(url_for('.member_list'))

# 숙소 정보 입력
@youth.route('/room_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def room_setting():
    member_idx = request.form.get('member_idx', 0)
    room_idx = request.form.get('idx', 0)
    Member.update(member_idx=member_idx, room_idx=room_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 지부 변경
@youth.route('/area_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def area_setting():
    member_idx = request.form.get('member_idx', 0)
    area_idx = request.form.get('area_idx', 0)
    Member.update(member_idx=member_idx, area_idx=area_idx)
    return redirect(url_for('.member', member_idx=member_idx))

# 단체 변경
@youth.route('/group_setting', methods=['POST'])
@login_required
@hq_permission.require(http_exception=403)
@youth_permission.require(http_exception=403)
def group_setting():
    member_idx = request.form.get('member_idx', 0)
    group_idx = request.form.get('group_idx', 0)
    Member.update(member_idx=member_idx, group_idx=group_idx)
    return redirect(url_for('.member', member_idx=member_idx))
