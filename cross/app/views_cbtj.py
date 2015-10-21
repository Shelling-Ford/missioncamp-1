#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *

cbtj = Blueprint('cbtj', __name__, template_folder='templates', url_prefix='/cbtj')

@cbtj.route('/')
def home():
    if not 'camp' in session or session['camp'] != 'cbtj' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cbtj')
    stat1 = get_basic_stat(camp_idx)

    camp_idx = getCampIdx('cbtj2')
    stat2 = get_basic_stat(camp_idx)
    return render_template('cbtj/home.html', stat1=stat1, stat2=stat2)

@cbtj.route('/list')
def member_list():
    if not 'camp' in session or session['camp'] != 'cbtj' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    camp = request.args.get('camp', 'cbtj')
    camp_idx = getCampIdx(camp)
    cancel_yn = int(request.args.get('cancel_yn', 0))

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn)
    return render_template('cbtj/list.html', members=member_list)
