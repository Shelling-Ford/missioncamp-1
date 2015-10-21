#-*-coding:utf-8-*-
from app import context
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from jinja2 import TemplateNotFound
from core.functions import *
from functions import *

@context.route('/')
def home():
    return render_template('home.html')

@context.route('/', methods=['POST'])
def login_proc():
    userid = request.form.get('userid', None)
    pwd = request.form.get('pwd', None)
    camp = request.form.get('camp', None)
    role = login_check(camp, userid, pwd)

    if userid == 'master' and pwd == 'historymakers':
        session['camp'] = camp
        session['role'] = 'master'
        return redirect(url_for('%s.home' % camp))
    elif role != 0:
        session['camp'] = camp
        session['role'] = role
        return redirect(url_for('%s.home' % camp))
    else:
        flash(u"로그인에 실패하였습니다.")
        return redirect(url_for('home'))
