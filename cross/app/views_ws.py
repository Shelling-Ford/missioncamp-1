#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.functions import *
from core.functions.ws import *
from functions import *
import functions_mongo as mongo
import xlsxwriter

# Blueprint 초기화
ws = Blueprint('ws', __name__, template_folder='templates', url_prefix='/ws')

master_permission = Permission(RoleNeed('master'))
hq_permission = Permission(RoleNeed('hq'))
branch_permission = Permission(RoleNeed('branch'))

# 메인 통계
@ws.route('/')
@login_required
@branch_permission.require(http_exception=403)
def home():
    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = getCampIdx('ws')
    else:
        camp_idx = getCampIdx('ws', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('ws/home.html', stat=stat)

# 신청자 목록
@ws.route('/list')
@login_required
@branch_permission.require(http_exception=403)
def member_list():
    camp_idx = getCampIdx('ws')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx)
    return render_template('ws/list.html', members=member_list)
