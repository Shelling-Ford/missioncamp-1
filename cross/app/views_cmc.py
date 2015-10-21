#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *

cmc = Blueprint('cmc', __name__, template_folder='templates', url_prefix='/cmc')

@cmc.route('/')
def home():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')
    stat = get_basic_stat(camp_idx)
    return render_template('cmc/home.html', stat=stat)

@cmc.route('/list')
def member_list():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')

    cancel_yn = int(request.args.get('cancel_yn', 0))

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn)
    return render_template('cmc/list.html', members=member_list)
