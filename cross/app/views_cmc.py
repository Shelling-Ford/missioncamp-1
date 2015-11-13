#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *
import functions_mongo as mongo

cmc = Blueprint('cmc', __name__, template_folder='templates', url_prefix='/cmc')

@cmc.route('/')
def home():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    year = int(request.args.get('year', 0))
    term = int(request.args.get('term', 0))

    if year == 0 or term == 0:
        camp_idx = getCampIdx('cmc')
    else:
        camp_idx = getCampIdx('cmc', year, term)

    stat = get_basic_stat(camp_idx)
    return render_template('cmc/home.html', stat=stat)

@cmc.route('/list')
def member_list():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))
    camp_idx = getCampIdx('cmc')

    cancel_yn = int(request.args.get('cancel_yn', 0))
    area_idx = request.args.get('area_idx', None)

    member_list = get_member_list(camp_idx, cancel_yn=cancel_yn, area_idx=area_idx)
    return render_template('cmc/list.html', members=member_list)

@cmc.route('/old-list')
def old_list():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    #campcode = request.args.get('campcode', None)

    #if campcode is not None:
    member_list = mongo.get_member_by_contact()

    return render_template("cmc/old_list.html", members=member_list)

@cmc.route('/old-member')
def old_member():
    if not 'camp' in session or session['camp'] != 'cmc' or not 'role' in session or not session['role'] in ['master', 'hq', 'branch']:
        flash(u"세션이 만료되었습니다. 다시 로그인해주세요")
        return redirect(url_for('home'))

    name = request.args.get('name', None)
    hp1 = request.args.get('hp1', None)

    if name is not None and hp1 is not None:
        member_list = mongo.get_member_list(name=name, hp1=hp1)
    return render_template("cmc/old_member.html", name=name, hp1=hp1, members=member_list)
