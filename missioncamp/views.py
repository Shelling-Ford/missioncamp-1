'''
세대별 캠프 뷰 공통부분을 관리하는 모듈.
'''
# pylint: disable=W0612,R0914
import datetime
from functools import wraps
from flask import Blueprint
from flask import render_template, request, flash, session, redirect, url_for
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from jinja2 import TemplateNotFound

from core.forms import RegistrationForm, GroupForm, RoomCheckForm
from core.models import Member, Area, Camp, Group, Promotion, Room
from core.database import DB as db


def login_required(logintype):
    '''
    해당 뷰가 로그인 필수 항목일 경우 이 함수를 데코레이터로 붙인다.
    logintype에 '개인' 또는 '단체' 로 지정하여 어떤 타입의 아이디로 로그인했는지 체크하도록 한다.
    '''
    def set_decorator(func):
        '''데코레이터.'''
        @wraps(func)
        def decorated_function(*args, **kwargs):
            '''검증 및 리다이렉트 수행.'''
            if 'type' in session and session['type'] == logintype and 'idx' in session:
                return func(*args, **kwargs)
            else:
                flash('로그인이 필요합니다. 먼저 로그인해주세요.')
                return redirect(url_for('.login', next=request.url))
        return decorated_function
    return set_decorator


def get_app(campcode):
    '''캠프 코드를 받아서 세대별 뷰를 등록하기 위한 블루프린트를 반환함.'''
    if campcode in ['cmc', 'cbtj', 'ws', 'kids', 'youth']:
        app = Blueprint(campcode, __name__, template_folder='templates',
                        url_prefix='/{0}'.format(campcode))
        register_view(app, campcode)
        return app
    else:
        return None


def register_view(app, campcode):
    '''
    블루프린트와 캠프코드를 받은 뒤에 뷰를 등록함.
    캠프코드에 따라서 뷰의 내용을 수정하고 해당 캠프의 템플릿으로 매칭함.
    '''

    # home - Main page for each Camp
    @app.route('/')
    def home():
        '''세대별 캠프의 첫 페이지.'''
        return render_template("{0}/home.html".format(campcode))

    # page - Static page for camp information
    @app.route('/<page_id>')
    def page(page_id):
        '''초대의 글, 추천의 글 등 정적 페이지로 이동할 때 사용.'''
        try:
            return render_template('{0}/{1}.html'.format(campcode, page_id))
        except TemplateNotFound:
            return render_template('{0}/404.html'.format(campcode))

    @app.route("/registration", methods=['GET', 'POST'])
    def registration():
        '''개인 신청.'''
        form = RegistrationForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            idx = form.insert()
            flash('신청이 완료되었습니다.')
            session['type'] = '개인'
            session['idx'] = idx
            return redirect(url_for('.member_info'))

        params = {
            'form': form,
            'page_header': "개인신청",
            'script': url_for('static', filename='{0}/js/reg-individual.js'.format(campcode))
        }
        return render_template('{0}/form.html'.format(campcode), **params)

    @app.route("/registration/edit", methods=['GET', 'POST'])
    @login_required(logintype='개인')
    def edit_registration():
        '''신청서 수정.'''
        idx = session['idx']
        form = RegistrationForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            form.update(idx)
            flash(u'수정이 완료되었습니다')
            return redirect(url_for('.member_info'))

        member = db.session.query(Member).filter(Member.idx == idx).one()
        form.set_member_data(member)

        params = {
            'form': form,
            'page_header': "개인 신청서 수정",
            'script': url_for('static', filename='{0}/js/reg-individual-edit.js'.format(campcode)),
            'editmode': True
        }
        return render_template('{0}/form.html'.format(campcode), **params)

    # pylint: disable=C0301
    @app.route("/member-info")
    @login_required(logintype='개인')
    def member_info():
        '''신청자 정보 보기.'''
        idx = session['idx']
        member = db.session.query(Member).filter(Member.idx == idx).one()
        params = {
            'camp': campcode,
            'member': member,
            'membership_data': member.get_membership_data(),
            'area_name': db.session.query(Area).filter(Area.idx == member.area_idx).one().name
        }
        return render_template('{0}/show.html'.format(campcode), **params)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        '''신청 조회 / 로그인하기.'''
        if request.method == 'POST':
            logintype = request.form.get('logintype', None)
            userid = request.form.get('userid', None)
            pwd = request.form.get('pwd', None)

            if logintype == '' or logintype is None:
                flash('신청 구분을 선택해주세요')
            elif userid == '' or userid is None:
                flash('아이디를 입력해주세요')
            elif pwd == '' or pwd is None:
                flash('비밀번호를 입력해 주세요')
            else:
                campidx = Camp.get_idx(campcode)
                if logintype == '개인':
                    if Member.login_check(campidx, userid, pwd):
                        idx = db.session.query(Member).filter(Member.camp_idx == campidx,
                                                              Member.userid == userid,
                                                              Member.cancel_yn == 0).one().idx
                        session['type'] = '개인'
                        session['idx'] = idx
                        return redirect(url_for('.member_info'))
                    else:
                        flash('아이디 또는 비밀번호가 잘못되었습니다.')
                elif logintype == '단체':
                    if Group.login_check(campidx, userid, pwd):
                        idx = db.session.query(Group).filter(Group.camp_idx == campidx,
                                                             Group.groupid == userid,
                                                             Group.cancel_yn == 0).one().idx
                        session['type'] = '단체'
                        session['idx'] = idx
                        return redirect(url_for('.group_info'))
                    else:
                        flash('아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('.login'))
        return render_template('{0}/check.html'.format(campcode))

    @app.route('/registration/cancel', methods=["GET", "POST"])
    @login_required(logintype='개인')
    def cancel_registration():
        '''신청 취소'''
        if request.method == "POST":
            cancel_reason = request.form.get('cancel_reason', None)
            idx = session['idx']
            member = db.session.query(Member).filter(Member.idx == idx).one()
            member.cancel_yn = 1
            member.cancel_reason = cancel_reason
            member.canceldate = datetime.datetime.today()
            db.session.commit()

            flash('신청이 취소되었습니다')
            return redirect(url_for('.home'))
        return render_template('{0}/cancel.html'.format(campcode))

    @app.route('/check-userid', methods=['POST'])
    @app.route('/group/member/check-userid', methods=['POST'])
    def check_userid():
        '''아이디 중복체크'''
        campidx = Camp.get_idx(campcode)
        userid = request.form.get('userid')
        return "%d" % Member.check_userid(campidx, userid)

    @app.route('/group/check-groupid', methods=['POST'])
    def check_groupid():
        '''단체아이디 중복체크'''
        campidx = Camp.get_idx(campcode)
        userid = request.form.get('groupid')
        return "%d" % Group.check_groupid(campidx, userid)

    @app.route('/group/registration', methods=["GET", "POST"])
    def reg_group():
        '''단체신청'''
        form = GroupForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            group_idx = form.insert(Camp.get_idx(campcode))

            session['type'] = '단체'
            session['idx'] = group_idx

            flash('신청이 완료되었습니다.')
            return redirect(url_for('.group_info'))

        script_file = 'common/js/reg-group.js'
        return render_template('{0}/form.html'.format(campcode),
                               form=form, page_header="단체신청",
                               script=url_for('static', filename=script_file))

    @app.route('/group/info')
    @login_required(logintype='단체')
    def group_info():
        '''단체신청 조회'''
        idx = session['idx']
        group = db.session.query(Group).filter(Group.idx == idx).one()
        member_list = db.session.query(Member).filter(Member.group_idx == idx, Member.cancel_yn == 0).all()
        area_name = db.session.query(Area).filter(Area.idx == group.area_idx).one().name
        return render_template('{0}/group/show.html'.format(campcode),
                               group=group, area=area_name, member_list=member_list)

    @app.route('/group/edit', methods=["GET", "POST"])
    @login_required(logintype='단체')
    def edit_group():
        '''단체 수정'''
        idx = session['idx']
        form = GroupForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            form.update(idx)
            flash("단체 정보 수정이 완료되었습니다.")
            return redirect(url_for('.group_info'))

        group = db.session.query(Group).filter(Group.idx == idx).one()
        form.set_group_data(group)
        script_file = 'common/js/reg-group-edit.js'
        return render_template('{0}/form.html'.format(campcode),
                               form=form, page_header="단체신청 수정",
                               script=url_for('static', filename=script_file),
                               editmode=True)

    @app.route('/group/cancel', methods=["GET", "POST"])
    @login_required(logintype='단체')
    def cancel_group():
        '''단체 취소'''
        if request.method == "POST":
            idx = session['idx']
            cancel_reason = request.form.get('cancel_reason', None)
            group = db.session.query(Group).filter(Group.idx == idx).one()
            group.cancel_yn = 1
            group.cancel_reason = cancel_reason
            group.canceldate = datetime.datetime.today()

            member_list = db.session.query(Member).filter(Member.group_idx == idx).all()

            for member in member_list:
                member.cancel_yn = 1
                member.cancel_reason = "단체취소: " + cancel_reason
                member.canceldate = datetime.datetime.today()

            db.session.commit()
            flash("단체 신청이 모두 취소되었습니다.")
            return redirect(url_for('.home'))
        return render_template('{0}/group/cancel.html'.format(campcode))

    @app.route('/group/member/add', methods=["GET", "POST"])
    @login_required(logintype='단체')
    def member_add():
        '''단체 멤버 추가'''
        idx = session['idx']
        group = db.session.query(Group).filter(Group.idx == idx).one()
        form = RegistrationForm(request.form)
        form.set_camp(campcode)
        form.set_group_mode(group_idx=idx, group_area_idx=group.area_idx)

        if request.method == "POST":
            form.insert()
            group.mem_num += 1
            db.session.commit()
            flash("멤버가 추가되었습니다.")
            return redirect(url_for(".group_info"))

        script_file = '{0}/js/reg-individual.js'.format(campcode)
        return render_template('{0}/form.html'.format(campcode),
                               form=form, page_header="멤버 추가",
                               script=url_for('static', filename=script_file))

    @app.route('/group/member/edit/<member_idx>', methods=["GET", "POST"])
    @login_required(logintype='단체')
    def member_edit(member_idx):
        '''단체 멤버 수정'''
        idx = session['idx']
        group = db.session.query(Group).filter(Group.idx == idx).one()
        form = RegistrationForm(request.form)
        form.set_camp(campcode)
        form.set_group_mode(group_idx=idx, group_area_idx=group.area_idx)

        if request.method == "POST":
            form.update(member_idx)
            flash("성공적으로 수정되었습니다.")
            return redirect(url_for(".group_info"))

        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        form.set_member_data(member)
        script_file = '{0}/js/reg-individual-edit.js'.format(campcode)
        return render_template('{0}/form.html'.format(campcode),
                               form=form, page_header="멤버 수정",
                               script=url_for('static', filename=script_file))

    @app.route('/group/member/cancel/<member_idx>', methods=["GET", "POST"])
    @login_required(logintype='단체')
    def member_cancel(member_idx):
        '''신청 취소'''
        if request.method == "POST":
            cancel_reason = request.form.get('cancel_reason', None)
            member = db.session.query(Member).filter(Member.idx == member_idx).one()
            member.cancel_yn = 1
            member.cancel_reason = cancel_reason
            member.canceldate = datetime.datetime.today()
            db.session.commit()

            idx = session['idx']
            group = db.session.query(Group).filter(Group.idx == idx).one()
            group.mem_num -= 1
            if group.mem_num < 0:
                group.mem_num = 0
            db.session.commit()

            flash('신청이 취소되었습니다')
            return redirect(url_for('.group_info'))
        return render_template('{0}/cancel.html'.format(campcode))

    @app.route('/logout')
    def logout():
        '''로그아웃'''
        session.clear()
        flash('정상적으로 로그아웃 되었습니다.')
        return redirect(url_for('.home'))

    @app.route('/promotion', methods=['POST'])
    def save_promotion_info():
        '''홍보물 신청'''
        camp_idx = Camp.get_idx(campcode)
        church_name = request.form.get('church_name', None)
        name = request.form.get('name', None)
        address = request.form.get('address', None)
        contact = request.form.get('contact', None)
        memo = request.form.get('memo', None)
        next_url = request.form.get('next', None)

        promotion = Promotion()
        promotion.camp_idx = camp_idx
        promotion.church_name = church_name
        promotion.name = name
        promotion.address = address
        promotion.contact = contact
        promotion.memo = memo
        db.session.add(promotion)
        db.session.commit()

        flash('홍보물 신청이 완료되었습니다')
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect(url_for('.home'))

    @app.route('/room-check', methods=['GET', 'POST'])
    def room_check():
        '''숙소확인'''
        form = RoomCheckForm(request.form)
        camp_idx = Camp.get_idx(campcode)
        if request.method == 'POST':
            contact = request.form.get('contact', '')
            name = request.form.get('name', '')
            logintype = request.form.get('logintype', '')

            if logintype == '개인':
                try:
                    member = db.session.query(Member).filter(
                        Member.name == name,
                        Member.contact == contact,
                        Member.camp_idx == camp_idx
                    ).one()

                    camp = db.session.query(Camp).filter(Camp.idx == camp_idx).one()

                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=member.name, camp=camp.name, msg=None, member_list=None)
                except MultipleResultsFound:
                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=None, camp=None, msg='중복신청오류입니다. 등록대에 문의해주세요.', member_list=None)
                except NoResultFound:
                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=None, camp=None, msg='신청자 정보가 없습니다.', member_list=None)

            elif logintype == '단체':
                try:
                    group = db.session.query(Group).filter(
                        Group.leadername == name,
                        Group.leadercontact == contact,
                        Group.camp_idx == camp_idx
                    ).one()

                    camp = db.session.query(Camp).filter(Camp.idx == camp_idx).one()
                    member_list = db.session.query(Member).filter(Member.group_idx == group.idx).all()

                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=Group.name, camp=camp.name, room=None, member_list=member_list)
                except MultipleResultsFound:
                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=None, camp=None, room=None, msg='중복신청오류입니다. 등록대에 문의해주세요.')
                except NoResultFound:
                    return render_template('{0}/room-check-result.html'.format(campcode),
                                           name=None, camp=None, room=None, msg='신청 단체 정보가 없습니다.')
        return render_template('{0}/room-check.html'.format(campcode), form=form)
