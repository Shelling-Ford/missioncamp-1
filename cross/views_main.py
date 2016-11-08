''' 크로스에서 로그인 및 인증 관련 절차를 처리하는 모듈
'''
# pylint: disable=W0612
from flask import render_template, flash, redirect, url_for, session, request
from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from cross.models import AdminUser, BtjUser
from core.models import Area
from core.database import BTJKOREA_DB as bkdb
from core.database import DB as db


def register_view(app):
    '''
    앱 또는 블루프린트에 뷰 등록
    '''
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "home"
    login_manager.login_message = "로그아웃 되었습니다. 먼저 로그인하시기 바랍니다."
    login_manager.login_message_category = "info"

    # flask-login login_manager
    @login_manager.user_loader
    def load_user(adminid):
        ''' Btjkorea 아이디로 로그인을 시도한 뒤에 실패할경우 Admin테이블에서 인증을 시도한다.
        '''
        user = db.session.query(AdminUser).filter(AdminUser.adminid == adminid).one()
        return user

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

            if bkdb.session.execute("SELECT count(*) FROM `g5_member` \
            WHERE mb_id = '{}' AND mb_password = PASSWORD('{}')".format(userid, pwd)).fetchone()[0] > 0:  # btjkorea 인증에 성공할경우
                try:
                    adminuser = db.session.query(AdminUser).filter(AdminUser.adminid == userid).one()
                except NoResultFound:
                    adminuser = AdminUser()

                btjuser = bkdb.session.query(BtjUser).filter(BtjUser.mb_id == userid).one()
                adminuser.adminid = userid
                adminuser.adminpw = pwd
                if btjuser.chaptercode == "01":
                    adminuser.role = 'hq'
                    adminuser.camp = 'cmc,cbtj,ws,youth,kids'
                else:
                    adminuser.role = 'branch'
                    adminuser.area_idx = db.session.query(Area).filter(Area.chaptercode == btjuser.chaptercode).first()
                    adminuser.camp = 'cmc,cbtj,ws,youth,kids'

                if adminuser.idx is None:
                    db.session.add(adminuser)

                db.session.commit()
                login_user(adminuser)

                return redirect(url_for('cmc.home'))
            elif db.session.query(AdminUser).filter(AdminUser.adminid == userid, AdminUser.adminpw == pwd).count() > 0:
                adminuser = db.session.query(AdminUser).filter(AdminUser.adminid == userid).one()

                login_user(adminuser)
                camp = adminuser.camp.split(',')[0]
                if camp == 'master':
                    camp = 'cmc'
                return redirect(url_for('%s.home' % camp))
            else:
                flash("아이디 또는 비밀번호가 잘못되었습니다.")
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
