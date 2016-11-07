''' 크로스에서 로그인 및 인증 관련 절차를 처리하는 모듈
'''
from flask import render_template, flash, redirect, url_for, session, request
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_loaded, RoleNeed
from cross.models import AdminUser, BtjUser
from core.models import Area


def register_view(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "home"
    login_manager.login_message = u"로그아웃 되었습니다. 먼저 로그인하시기 바랍니다."
    login_manager.login_message_category = "info"

    # principal 초기화
    principals = Principal(app)

    # flask-login login_manager
    @login_manager.user_loader
    def load_user(adminid):
        ''' Btjkorea 아이디로 로그인을 시도한 뒤에 실패할경우 Admin테이블에서 인증을 시도한다.
        '''
        try:
            user = BtjUser.get(mb_id=adminid)
        except:
            user = AdminUser.get(id=adminid)

        return user

    # flask-principal
    @principals.identity_loader
    def read_identity_from_flask_login():
        ''' 로그인 사용자 아이디에 따라서 권한을 부여한다.
        '''
        if current_user.is_authenticated:
            try:
                return Identity(current_user.mb_id)
            except:
                return Identity(current_user.adminid)
        return AnonymousIdentity()

    # flask-principal
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        ''' 아이디별 세부 권한 부여
        '''
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
                print(camp_list)
                for camp in camp_list:
                    identity.provides.add(RoleNeed(camp))
            if current_user.role == 'branch':
                identity.provides.add(RoleNeed('branch'))
                identity.provides.add(RoleNeed(current_user.camp))

    @app.route('/', methods=['GET', 'POST'])
    def home():
        ''' 로그인 되었을 경우 캠프별 랜딩페이지로 이동하고 로그인되지 않았을 경우 로그인 폼을 보여준다.
        '''
        if current_user.is_authenticated:
            camp = current_user.camp
            return redirect(url_for('%s.home' % camp))

        if request.method == 'POST':
            userid = request.form.get('userid', None)
            pwd = request.form.get('pwd', None)

            if BtjUser.login_check(userid, pwd):
                btjuser = BtjUser.get(mb_id=userid)

                if btjuser.chaptercode == "01":
                    btjuser.role = 'hq'
                else:
                    btjuser.role = 'branch'
                    btjuser.area_idx = Area.get_idx(btjuser.chaptercode)
                    btjuser.camp = 'cmc'
                    login_user(btjuser)

                camp = 'cmc'
                return redirect(url_for('%s.home' % camp))
            elif AdminUser.login_check(userid, pwd):
                adminuser = AdminUser.get(id=userid)

                login_user(adminuser)
                camp = adminuser.camp.split(',')[0]
                if camp == 'master':
                    camp = 'cmc'
                return redirect(url_for('%s.home' % camp))
            else:
                flash(u"아이디 또는 비밀번호가 잘못되었습니다.")
                return redirect(url_for('home'))
        return render_template('home.html')

    @app.route('/logout')
    def logout():
        ''' 로그아웃
        '''
        logout_user()
        session.clear()
        flash('로그아웃 되었습니다.')
        return redirect(url_for('home'))
