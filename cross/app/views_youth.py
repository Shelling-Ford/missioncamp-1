#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *

youth = Blueprint('youth', __name__, template_folder='templates', url_prefix='/youth')

@youth.route('/')
def home():
    if not 'camp' in session or session['camp'] != 'youth' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = getCampIdx('youth')
    else:
        camp_idx = getCampIdx('youth', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('youth/home.html', stat=stat)

@youth.route('/list')
def member_list():
    if not 'camp' in session or session['camp'] != 'youth' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('youth')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx)
    return render_template('youth/list.html', members=member_list)
