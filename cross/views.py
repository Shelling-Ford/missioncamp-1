'''
세대별 크로스 뷰 공통부분을 관리하는 모듈
'''
# pylint: disable=W0612,C0301,R0912,R0914,C0413
import datetime
from functools import wraps
from flask import Blueprint
from flask import request, render_template, redirect, abort, url_for, session, flash
from flask.helpers import make_response
from flask_login import login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc, or_

from core.forms import RegistrationForm, GroupForm
from core.database import DB as db
from core.models import Area, Camp, Member, Group, Room, Roomsetting, Payment, Promotion
from cross.functions_xlsx import XlsxBuilder
from cross import statistics
from cross.stat_metrics import METRICS as metrics


def role_required(role, camp='*'):
    '''
    해당 뷰가 권한을 요구할 경우 이 함수를 데코레이터로 붙인다.
    role에 'hq' 또는 'branch'를 지정하고 camp에 campcode를 지정하여 그 외의 권한을 제한한다.
    '''
    def set_decorator(func):
        '''
        데코레이터
        '''
        @wraps(func)
        def decorated_function(*args, **kwargs):
            '''
            검증 및 리다이렉트 수행
            '''
            if current_user.role == 'master':
                return func(*args, **kwargs)

            if role == 'hq':
                if current_user.role not in ['hq', 'master'] or camp not in ['*', *current_user.camp.split(',')]:
                    flash('이 페이지에 대한 접근 권한이 없습니다.')
                    return redirect(url_for('.home', next=request.url))
                else:
                    return func(*args, **kwargs)
            else:
                if camp not in ["*", *current_user.camp.split(',')]:
                    flash('이 페이지에 대한 접근 권한이 없습니다.')
                    return redirect(url_for('.home', next=request.url))
                else:
                    return func(*args, **kwargs)
        return decorated_function
    return set_decorator


def get_member_list_query(query, req, orderby=None):
    '''
    특정 필터를 적용하여 멤버 목록을 데이터베이스로부터 가져올 때 사용하는 쿼리
    '''
    filtered_query = query

    # filters
    cancel_yn = req.args.get('cancel_yn', 0)
    filtered_query = filtered_query.filter(Member.cancel_yn == cancel_yn)

    area_idx = req.args.get('area_idx', None)
    user_area_idx = current_user.area_idx
    print(user_area_idx)
    if user_area_idx is not None:
        '''
        비티제이 코리아 지부 아이디는 자기 지부 목록만 조회 가능
        '''
        area_idx = user_area_idx

    if area_idx not in [None, '']:
        filtered_query = filtered_query.filter(Member.area_idx == area_idx)

    name = req.args.get('name', None)
    if name not in [None, '']:
        filtered_query = filtered_query.filter(Member.name.like("%{}%".format(name)))

    for key in ['persontype', 'sex']:
        value = req.args.get(key, None)
        if value not in [None, '']:
            filtered_query = filtered_query.filter(getattr(Member, key) == value)

    for key in ['group_idx', 'room_idx']:
        value = req.args.get(key, None)
        if value not in [None, '']:
            if value == 'none' or value == 'None':
                filtered_query = filtered_query.filter(getattr(Member, key).is_(None))
            elif value == 'not_none':
                filtered_query = filtered_query.filter(getattr(Member, key).isnot(None))
            else:
                filtered_query = filtered_query.filter(getattr(Member, key) == value)

    for key in ['training', 'job', 'campus', 'major', 'job_name']:
        value = req.args.get(key, None)
        if value not in [None, '']:
            filtered_query = filtered_query.filter(Member.membership.any(value=value))

    complete_list = request.args.getlist('complete', None)
    if complete_list is not None and len(complete_list) > 0:
        filtered_query = filtered_query.filter(*[Member.payment.has(complete=complete) for complete in complete_list])

    # order_by
    if orderby is None:
        filtered_query = filtered_query.order_by(desc(Member.idx))
    else:
        orderby = orderby if isinstance(orderby, list) else [orderby]
        filtered_query = filtered_query.order_by(*[desc(getattr(Member, o)) for o in orderby])

    return filtered_query


def get_app(campcode):
    '''
    캠프 코드를 받아서 세대별 뷰를 등록하기 위한 블루프린트를 반환함.
    '''
    if campcode in ['cmc', 'cbtj', 'ws', 'kids', 'youth']:
        app = Blueprint(campcode, __name__, template_folder='templates', url_prefix='/{0}'.format(campcode))
        register_view(app, campcode)
        return app
    else:
        return None


def register_view(app, campcode):
    '''
    블루프린트와 캠프코드를 받은 뒤에 뷰를 등록함. 캠프코드에 따라서 뷰의 내용을 수정하고
    해당 캠프의 템플릿으로 매칭함.
    '''
    @app.route('/')
    @login_required
    def home():
        '''
        각 캠프의 전체 통계를 보여주는 페이지
        '''
        year = int(request.args.get('year', 0))
        term = int(request.args.get('term', 0))
        camp_idx = Camp.get_idx(campcode, year, term)

        area_idx = request.args.get('area_idx', None)
        if area_idx is not None and area_idx != current_user.area_idx:
            area_idx = current_user.area_idx

        stat = statistics.get_stat(camp_idx, area_idx=area_idx)
        attend_stat = Member.get_attend_stat(camp_idx)
        partial_stat = Member.get_partial_stat(camp_idx)

        fromdate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=20), "%Y-%m-%d")

        query = """
            SELECT DATE(regdate) AS ForDate, COUNT(*) AS NumMembers FROM
            member WHERE regdate >= '{0}' AND camp_idx = {1} GROUP BY DATE(regdate)
            ORDER BY ForDate
        """.format(fromdate, camp_idx)

        daily_apply = db.session.execute(query)
        chart = None

        return render_template('{0}/home.html'.format(campcode), stat=stat, metrics=metrics,
                               attend_stat=attend_stat, partial_stat=partial_stat, chart=chart, daily_apply=daily_apply)

    @app.route('/list')
    @login_required
    def member_list():
        '''
        신청자목록
        '''
        year = request.args.get('year', 0)
        term = request.args.get('term', 0)
        camp_idx = Camp.get_idx(campcode, year, term)
        receptionmode = request.args.get('receptionmode', False)

        query = db.session.query(Member)
        if (campcode == 'cmc' or campcode == 'cbtj') and receptionmode:
            cmc_idx = Camp.get_idx('cmc')
            cbtj_idx = Camp.get_idx('cbtj')
            filtered_query = query.filter(or_(Member.camp_idx == cmc_idx, Member.camp_idx == cbtj_idx))
        else:
            filtered_query = query.filter(Member.camp_idx == camp_idx)

        filtered_query = get_member_list_query(filtered_query, request)

        # pagination
        page = int(request.args.get('page', 1))
        count = filtered_query.count()
        filtered_query = filtered_query.limit(50).offset((page - 1) * 50)
        member_list = filtered_query.all()

        group_idx = request.args.get('group_idx', None)
        if group_idx not in [None, '', 'none', 'not_none']:
            group = db.session.query(Group).filter(Group.idx == group_idx).one()
        else:
            group = None

        area_list = Area.get_list(campcode)
        group_list = db.session.query(Group).filter(Group.camp_idx == camp_idx).all()
        return render_template('%s/list.html' % campcode, members=member_list,
                               group=group, count=count - (page - 1) * 50,
                               nav=range(1, int(count / 50) + 2),
                               area_list=area_list, group_list=group_list)

    @app.route('/toggle-attend')
    @login_required
    @role_required('hq')
    def toggle_attend():
        '''
        출석체크
        '''
        member_idx = request.args.get('member_idx')
        attend = request.args.get('attend', 0)

        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.attend_yn = attend
        if attend == "1":
            member.attend_time = datetime.datetime.today()
        else:
            member.attend_time = None
        db.session.commit()

        next_url = request.args.get('next')
        return redirect(next_url)

    @app.route('/member/<member_idx>')
    @login_required
    def member(member_idx):
        '''
        신청자 상세
        '''
        if member_idx != 0:
            member = db.session.query(Member).filter(Member.idx == member_idx).one()
            camp_idx = member.camp_idx
            room_list = db.session.query(Room).all()
            area_list = Area.get_list(campcode)
            group_list = db.session.query(Group).filter(Group.camp_idx == camp_idx).all()

            return render_template('%s/member.html' % campcode, member=member,
                                   room_list=room_list, area_list=area_list,
                                   group_list=group_list, membership=member.get_membership_data())
        else:
            abort(404)

    @app.route('/member/<member_idx>/edit', methods=['GET', 'POST'])
    @login_required
    @role_required('branch', campcode)
    def member_edit(member_idx):
        '''
        신청서 수정
        '''
        form = RegistrationForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            form.update(member_idx)
            flash('수정이 완료되었습니다')
            return redirect(url_for('.member', member_idx=member_idx))

        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        form.set_member_data(member)

        params = {
            'form': form,
            'page_header': "개인 신청서 수정",
            'script': url_for('static', filename='{0}/js/reg-individual-edit.js'.format(campcode)),
            'editmode': True
        }
        return render_template('{0}/form.html'.format(campcode), **params)

    @app.route('/group/<group_idx>/edit', methods=['GET', 'POST'])
    @login_required
    @role_required('branch', campcode)
    def group_edit(group_idx):
        '''
        신청서 수정
        '''
        form = GroupForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            form.update(group_idx)
            flash('수정이 완료되었습니다')
            return redirect(url_for('.member_list'))

        group = db.session.query(Group).filter(Group.idx == group_idx).one()
        form.set_group_data(group)

        params = {
            'form': form,
            'page_header': "단체 정보 수정",
            # 'script': url_for('static', filename='{0}/js/reg-individual-edit.js'.format(campcode)),
            'editmode': True
        }
        return render_template('{0}/form.html'.format(campcode), **params)

    @app.route('/pay', methods=['POST'])
    @login_required
    @role_required('hq')
    def pay():
        '''
        입금 정보 입력
        '''
        member_idx = request.args.get('member_idx', 0)
        amount = request.form.get('amount')
        complete = request.form.get('complete')
        claim = request.form.get('claim')
        paydate = request.form.get('paydate')
        staff_name = request.form.get('staff_name')

        try:
            payment = db.session.query(Payment).filter(Payment.member_idx == member_idx).one()
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.paydate = paydate
            payment.staff_name = staff_name
        except NoResultFound:
            payment = Payment()
            payment.member_idx = member_idx
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.paydate = paydate
            payment.staff_name = staff_name
            db.session.add(payment)
        db.session.commit()

        next_url = request.form.get('next', None)
        if next_url is not None:
            return redirect(next_url)

        return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/delpay')
    @login_required
    @role_required('hq')
    def delpay():
        '''
        입금정보 삭제
        '''
        member_idx = request.args.get('member_idx', 0)
        try:
            payment = db.session.query(Payment).filter(Payment.member_idx == member_idx).one()
            db.session.delete(payment)
            db.session.commit()
        except NoResultFound:
            pass

        return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/room-setting', methods=['POST'])
    @login_required
    @role_required('hq')
    def room_setting():
        '''
        숙소정보 입력
        '''
        member_idx = request.form.get('member_idx', 0)
        room_idx = request.form.get('idx', 0)
        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.room_idx = room_idx
        db.session.commit()

        next_url = request.args.get('next')
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/room-cancel')
    @login_required
    @role_required('hq')
    def room_cancel():
        '''
        숙소배치정보 삭제
        '''
        member_idx = request.args.get('member_idx', 0)
        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.room_idx = None
        db.session.commit()

        next_url = request.args.get('next')
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/area-setting', methods=['POST'])
    @login_required
    @role_required('hq')
    def area_setting():
        '''
        지부설정
        '''
        member_idx = request.form.get('member_idx', 0)
        area_idx = request.form.get('area_idx', 0)
        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.area_idx = area_idx
        db.session.commit()

        next_url = request.args.get('next')
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/group-setting', methods=['POST'])
    @login_required
    @role_required('hq')
    def group_setting():
        '''
        단체 변경
        '''
        member_idx = request.form.get('member_idx', 0)
        group_idx = request.form.get('group_idx', 0)
        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.group_idx = group_idx
        db.session.commit()

        next_url = request.args.get('next')
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect(url_for('.member', member_idx=member_idx))

    @app.route('/member-cancel', methods=['GET', 'POST'])
    @login_required
    @role_required('hq')
    def member_cancel():
        '''
        신청취소
        '''
        member_idx = request.args.get('member_idx', 0)
        session['idx'] = member_idx

        if request.method == 'POST':
            cancel_reason = request.form.get('cancel_reason', None)
            idx = session['idx']
            member = db.session.query(Member).filter(Member.idx == member_idx).one()
            member.cancel_yn = 1
            member.cancel_reason = cancel_reason
            member.attend1 = 0
            member.attend2 = 0
            member.attend3 = 0
            member.attend4 = 0
            db.session.commit()
            flash('신청이 취소되었습니다')
            return redirect(url_for('.member_list', cancel_yn=1))

        return render_template('%s/member_cancel.html' % campcode)

    @app.route('/member-recover')
    @login_required
    @role_required('hq')
    def member_recover():
        '''
        신청 복원
        '''
        member_idx = request.args.get('member_idx')
        member = db.session.query(Member).filter(Member.idx == member_idx).one()
        member.cancel_yn = 0
        db.session.commit()
        flash('신청이 복원되었습니다')
        return redirect(url_for('.member_list'))

    @app.route('/roomasign', methods=['POST', 'GET'])
    @login_required
    @role_required('hq')
    def roomassign():
        '''
        숙소 배정
        '''
        if request.method == 'POST':
            member_list = request.form.getlist('member_idx')
            room_idx = request.form.get('room_idx')

            for member_idx in member_list:
                member = db.session.query(Member).filter(Member.idx == member_idx).one()
                member.room_idx = room_idx

            db.session.commit()

            next_url = request.args.get('next')
            if next_url is not None:
                return redirect(next_url)
            else:
                return redirect(url_for('.roomassign'))

        camp_idx = Camp.get_idx(campcode)
        query = db.session.query(Member)
        if campcode == 'cmc' or campcode == 'cbtj':
            cmc_idx = Camp.get_idx('cmc')
            cbtj_idx = Camp.get_idx('cbtj')
            room_stat = Room.get_stat(camp_idx=[cmc_idx, cbtj_idx])
            filtered_query = query.filter(or_(Member.camp_idx == cmc_idx, Member.camp_idx == cbtj_idx))
            room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == cmc_idx).all()
        else:
            filtered_query = query.filter(Member.camp_idx == camp_idx)
            room_stat = Room.get_stat(camp_idx=camp_idx)
            room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == camp_idx).all()

        filtered_query = get_member_list_query(filtered_query, request, orderby=['camp_idx', 'sex', 'area_idx'])

        page = int(request.args.get('page', 1))
        filtered_query = filtered_query.limit(50).offset((page - 1) * 50)
        member_list = filtered_query.all()
        count = filtered_query.count()

        area_list = Area.get_list(campcode)
        group_list = db.session.query(Group).filter(Group.camp_idx == camp_idx).all()
        return render_template('%s/room_assign.html' % campcode, room_list=room_list,
                               members=member_list, count=count - (page - 1) * 50,
                               nav=range(1, int(count / 50) + 2), area_list=area_list,
                               group_list=group_list, room_stat=room_stat)

    @app.route('/room', methods=['POST', 'GET'])
    @login_required
    @role_required('hq')
    def room():
        '''
        숙소 현황
        '''
        if request.method == 'POST':
            member_list = request.form.getlist('member_idx')
            for member_idx in member_list:
                member = db.session.query(Member).filter(Member.idx == member_idx).one()
                member.room_idx = None
                db.session.commit()

            next_url = request.args.get('next')
            if next_url is not None:
                return redirect(next_url)
            else:
                return redirect(url_for('.room'))
        else:
            camp_idx = Camp.get_idx(campcode)
            query = db.session.query(Member)
            if campcode == 'cmc' or campcode == 'cbtj':
                cmc_idx = Camp.get_idx('cmc')
                cbtj_idx = Camp.get_idx('cbtj')
                filtered_query = query.filter(or_(Member.camp_idx == cmc_idx, Member.camp_idx == cbtj_idx))
                room_stat = Room.get_stat(camp_idx=[cmc_idx, cbtj_idx])
                room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == cmc_idx).all()
            else:
                filtered_query = query.filter(Member.camp_idx == camp_idx)
                room_stat = Room.get_stat(camp_idx=camp_idx)
                room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == camp_idx).all()

            filtered_query = get_member_list_query(filtered_query, request, orderby=['camp_idx', 'sex', 'area_idx'])

            page = int(request.args.get('page', 1))
            filtered_query = filtered_query.limit(50).offset((page - 1) * 50)

            if request.args.get('room_idx', None) is not None:
                member_list = filtered_query.all()
                count = filtered_query.count()
            else:
                member_list = []
                count = 0

            area_list = Area.get_list(campcode)
            group_list = db.session.query(Group).filter(Group.camp_idx == camp_idx).all()

            return render_template('%s/room.html' % campcode, room_list=room_list,
                                   members=member_list, count=count, area_list=area_list,
                                   group_list=group_list, room_stat=room_stat)

    @app.route('/roomsetting', methods=['POST', 'GET'])
    @login_required
    @role_required('hq')
    def roomsetting():
        '''
        캠프별 숙소 셋팅
        '''
        if request.method == 'POST':
            params = request.form.to_dict()
            for key, value in params.items():
                k = key.split('-')
                roomsetting = db.session.query(Roomsetting).filter(Roomsetting.idx == k[1]).one()
                setattr(roomsetting, k[0], value)
                db.session.commit()
                # roomsetting.save()

        camp_idx = Camp.get_idx(campcode)
        room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == camp_idx).all()
        if room_list is None or len(room_list) == 0:
            Roomsetting.init(camp_idx)
            room_list = db.session.query(Roomsetting).filter(Roomsetting.camp_idx == camp_idx).all()

        return render_template('%s/room_setting.html' % campcode, room_list=room_list)

    @app.route('/fix-attend-error')
    @login_required
    @role_required('hq')
    def fix_attend_error():
        '''
        참가기간 통계표 수정
        '''
        Member.fix_attend_error(Camp.get_idx(campcode))
        next_url = request.args.get('next', url_for('.home'))
        return redirect(next_url)

    # 엑셀 다운로드
    @app.route('/excel-down', methods=['GET'])
    @login_required
    @role_required('hq', campcode)
    def excel_down():
        '''
        엑셀다운로드
        '''
        year = request.args.get('year', 0)
        term = request.args.get('term', 0)

        camp_idx = Camp.get_idx(campcode, year=year, term=term)
        query = db.session.query(Member)
        filtered_query = query.filter(Member.camp_idx == camp_idx)
        filtered_query = get_member_list_query(filtered_query, request)
        member_list = filtered_query.all()

        xlsx_builder = XlsxBuilder()
        output = xlsx_builder.get_document(campcode, member_list)
        response = make_response(output.read())
        response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
        return response

    @app.route('/promotion-list')
    @login_required
    def promotion_list():
        '''
        홍보물 신청 리스트
        '''
        camp_idx = Camp.get_idx(campcode)
        promotion_list = db.session.query(Promotion).filter(Promotion.camp_idx == camp_idx).all()
        return render_template('%s/promotion_list.html' % campcode, promotions=promotion_list)
