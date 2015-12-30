# -*-coding:utf-8-*-
from app import context
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_loaded, RoleNeed

from core.functions import *
from functions import *
from models import AdminUser


login_manager = LoginManager()
login_manager.init_app(context)
login_manager.login_view = "home"
login_manager.login_message = u"로그아웃 되었습니다. 먼저 로그인하시기 바랍니다."
login_manager.login_message_category = "info"

# principal 초기화
principals = Principal(context)

# flask-login login_manager
@login_manager.user_loader
def load_user(adminid):
    return AdminUser.get(adminid)

# flask-principal
@principals.identity_loader
def read_identity_from_flask_login():
    if current_user.is_authenticated:
        return Identity(current_user.adminid)
    return AnonymousIdentity()

# flask-principal
@identity_loaded.connect_via(context)
def on_identity_loaded(sender, identity):
    if not isinstance(identity, AnonymousIdentity):
        if current_user.role == 'master':
            identity.provides.add(RoleNeed('master'))
            identity.provides.add(RoleNeed('hq'))
            identity.provides.add(RoleNeed('branch'))
            identity.provides.add(RoleNeed('cmc'))
            identity.provides.add(RoleNeed('cbtj'))
            identity.provides.add(RoleNeed('ws'))
            identity.provides.add(RoleNeed('youth'))
            identity.provides.add(RoleNeed('kids'))
        if current_user.role == 'hq':
            identity.provides.add(RoleNeed('hq'))
            identity.provides.add(RoleNeed('branch'))
            camp_list = current_user.camp.split(',')
            print camp_list
            for camp in camp_list:
                identity.provides.add(RoleNeed(camp))
        if current_user.role == 'branch':
            identity.provides.add(RoleNeed('branch'))
            identity.provides.add(RoleNeed(current_user.camp))


# 로그인 폼
@context.route('/')
def home():
    if current_user.is_authenticated:
        camp = current_user.camp
        return redirect(url_for('%s.home' % camp))

    return render_template('home.html')


# 로그인 검증
@context.route('/', methods=['POST'])
def login_proc():
    userid = request.form.get('userid', None)
    pwd = request.form.get('pwd', None)

    adminuser = AdminUser.get(userid)
    if adminuser is not None and pwd == adminuser.adminpw:
        login_user(adminuser)
        camp = adminuser.camp.split(',')[0]
        return redirect(url_for('%s.home' % camp))
    else:
        flash(u"아이디 또는 비밀번호가 잘못되었습니다.")
        return redirect(url_for('home'))


# 로그아웃
@context.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash(u'로그아웃 되었습니다.')
    return redirect(url_for('home'))
