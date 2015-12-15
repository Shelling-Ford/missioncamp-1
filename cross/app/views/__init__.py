# -*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint, abort
from flask.helpers import make_response
from flask_login import login_required  # , current_user
from flask_principal import Permission, RoleNeed
# from jinja2 import TemplateNotFound

from core.models import Group, Member, Camp, Area, Room, Payment, Promotion
from core.functions import *
from app.functions import *

from app import functions_mongo as mongo
from app import functions_xlsx as xlsx
from app.functions_xlsx import XlsxBuilder
# import xlsxwriter


class MetaView():
    def init_home(self):
        # 메인통계
        @self.context.route('/')
        @login_required
        def home():
            year = int(request.args.get('year', 0))
            term = int(request.args.get('term', 0))
            camp_idx = Camp.get_idx(self.camp, year, term)
            stat = get_basic_stat(camp_idx)
            return render_template('%s/home.html' % self.camp, stat=stat)
        pass

    def init_member_list(self):
        # 신청자 목록
        @self.context.route('/list')
        @login_required
        def member_list():
            camp_idx = Camp.get_idx(self.camp)
            group_idx = request.args.get('group_idx', None)
            page = int(request.args.get('page', 1))
            group = Group.get(group_idx) if group_idx is not None else None

            params = request.args.to_dict()
            if 'page' not in params:
                params['page'] = page

            member_list = Member.get_list(camp_idx, **params)
            count = Member.count(camp_idx, **params)
            area_list = Area.get_list(self.camp)
            group_list = Group.get_list(camp_idx)
            return render_template(
                '%s/list.html' % self.camp, members=member_list, group=group, count=count-(page-1)*50,
                nav=range(1, int(count/50)+2), area_list=area_list, group_list=group_list
            )
        pass

    def __init__(self, camp):
        self.camp = camp
        self.context = Blueprint(self.camp, __name__, template_folder='templates', url_prefix='/%s' % self.camp)
        self.hq_permission = Permission(RoleNeed('hq'))
        self.camp_permission = Permission(RoleNeed(self.camp))

        # 신청자 상세
        @self.context.route('/member')
        @login_required
        def member():
            camp_idx = Camp.get_idx(self.camp) if self.camp != 'cbtj' else Camp.get_idx(request.args.get('camp'))

            member_idx = request.args.get('member_idx', 0)

            if member_idx != 0:
                member = Member.get(member_idx)
                room_list = Room.get_list()
                area_list = Area.get_list(self.camp)
                group_list = Group.get_list(camp_idx)

                return render_template(
                    '%s/member.html' % self.camp, member=member, room_list=room_list, area_list=area_list,
                    group_list=group_list, membership=member.get_membership_data()
                )
            else:
                abort(404)

        # 입금 정보 입력
        @self.context.route('/pay', methods=['POST'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def pay():
            member_idx = request.args.get('member_idx', 0)
            amount = request.form.get('amount')
            complete = request.form.get('complete')
            claim = request.form.get('claim')
            paydate = request.form.get('paydate')
            staff_name = request.form.get('staff_name')

            Payment.save(member_idx=member_idx, amount=amount, complete=complete, claim=claim, paydate=paydate, staff_name=staff_name)

            next = request.form.get('next', None)
            if next is not None:
                return redirect(next)

            return redirect(url_for('.member', member_idx=member_idx))

        # 입금 정보 삭제
        @self.context.route('/delpay')
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def delpay():
            member_idx = request.args.get('member_idx', 0)
            Payment.delete(member_idx)
            return redirect(url_for('.member', member_idx=member_idx))

        # 숙소 정보 입력
        @self.context.route('/room_setting', methods=['POST'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def room_setting():
            member_idx = request.form.get('member_idx', 0)
            room_idx = request.form.get('idx', 0)
            Member.update(member_idx=member_idx, room_idx=room_idx)
            next = request.args.get('next')
            if next is not None:
                return redirect(next)
            else:
                return redirect(url_for('.member', member_idx=member_idx))

        # 지부 변경
        @self.context.route('/area_setting', methods=['POST'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def area_setting():
            member_idx = request.form.get('member_idx', 0)
            area_idx = request.form.get('area_idx', 0)
            Member.update(member_idx=member_idx, area_idx=area_idx)
            next = request.args.get('next')
            if next is not None:
                return redirect(next)
            else:
                return redirect(url_for('.member', member_idx=member_idx))

        # 단체 변경
        @self.context.route('/group_setting', methods=['POST'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def group_setting():
            member_idx = request.form.get('member_idx', 0)
            group_idx = request.form.get('group_idx', 0)
            Member.update(member_idx=member_idx, group_idx=group_idx)
            next = request.args.get('next')
            if next is not None:
                return redirect(next)
            else:
                return redirect(url_for('.member', member_idx=member_idx))

        # 엑셀 다운로드
        @self.context.route('/excel-down', methods=['GET'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def excel_down():
            camp_idx = getCampIdx(self.camp)
            # output = xlsx.get_document(camp_idx, **request.args.to_dict())
            xlsx_builder = XlsxBuilder()
            output = xlsx_builder.get_document(camp_idx, **request.args.to_dict())
            response = make_response(output.read())
            response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
            return response

        # 신청 취소
        @self.context.route('/member-cancel')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_cancel():
            member_idx = request.args.get('member_idx', 0)
            session['idx'] = member_idx
            return render_template('%s/member_cancel.html' % self.camp)

        # 신청 취소 적용
        @self.context.route('/member-cancel', methods=['POST'])
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_cancel_proc():
            cancel_reason = request.form.get('cancel_reason', None)
            idx = session['idx']
            Member.update(idx, cancel_yn=1, cancel_reason=cancel_reason)
            flash(u'신청이 취소되었습니다')
            return redirect(url_for('.member_list', cancel_yn=1))

        # 신청 취소 복원
        @self.context.route('/member-recover')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_recover():
            member_idx = request.args.get('member_idx')
            Member.update(member_idx, cancel_yn=0)
            flash(u'신청이 복원되었습니다')
            return redirect(url_for('.member_list'))

        # 출석체크
        @self.context.route('/toggle-attend')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def toggle_attend():
            member_idx = request.args.get('member_idx')
            attend = request.args.get('attend', 0)
            Member.update(member_idx, attend_yn=attend)
            next = request.args.get('next')
            return redirect(next)

        # 이전 참가자 리스트
        @self.context.route('/old-list')
        @login_required
        def old_list():
            year = int(request.args.get('year', 0))
            term = int(request.args.get('term', 0))

            skip = int(request.args.get('page', 1)) * 50 - 50
            name = request.args.get('name', None)
            area = request.args.get('area', None)
            camp = request.args.get('camp', 'cmc')

            if year == 0 or term == 0:
                camp = None if camp == 'cmc' else camp
                campcode = request.args.get('campcode', None)
                member_list = mongo.get_member_list_with_count(skip=skip, campcode=campcode, name=name, area=area, camp=camp)
                count = mongo.get_member_count(campcode=campcode, name=name, area=area, camp=camp)
                return render_template(
                    "%s/old_list.html" % self.camp, members=member_list, name=name, area=area, campcode=campcode, count=range(1, int(count/50)+2)
                )
            else:
                camp_idx = Camp.get_idx(camp, year, term)
                area_idx = request.args.get('area_idx', None)
                member_list = Member.get_old_list(camp_idx=camp_idx, name=name, offset=skip, area_idx=area_idx)
                member_count = Member.count(camp_idx=camp_idx, name=name, area_idx=area_idx)

                for member in member_list:
                    count = mongo.db.count({"hp1": member.contact, "name": member.name, "entry": "Y", "fin": {"$ne": "d"}})
                    count += Member.count(camp_idx=camp_idx, name=member.name, contact=member.contact, attend_yn=1, cancel_yn=0)
                    setattr(member, 'count', count)

                return render_template(
                    "%s/old_list_2.html" % self.camp, members=member_list, camp=camp, year=year, term=term, name=name,
                    count=range(1, int(member_count/50)+2)
                )

        # 이전 참가자 상세
        @self.context.route('/old-member')
        @login_required
        def old_member():
            name = request.args.get('name', None)
            hp1 = request.args.get('hp1', None)

            if name is not None and hp1 is not None:
                member_list = mongo.get_member_list(name=name, hp1=hp1)
                logs = mongo.get_member_call_logs(name=name, hp1=hp1)

            return render_template("%s/old_member.html" % self.camp, name=name, hp1=hp1, members=member_list, logs=logs)

        # 통화내용 저장
        @self.context.route('/save-log', methods=['POST'])
        @login_required
        def save_log():
            name = request.form.get('name', None)
            hp1 = request.form.get('hp1', None)
            log = request.form.get('log', None)
            date = datetime.datetime.today()

            mongo.save_member_call_log(name=name, hp1=hp1, log=log, date=date)
            return redirect(url_for('.old_member', name=name, hp1=hp1))

        # 이전 통계
        @self.context.route('/old-stat')
        @login_required
        def old_stat():
            year = int(request.args.get('year', 0))
            term = int(request.args.get('term', 0))

            if year == 0 or term == 0:
                campcode = request.args.get('campcode', None)
                stat = mongo.get_basic_stat(campcode)
                return render_template('%s/old_stat.html' % self.camp, stat=stat, campcode=campcode)
            else:
                camp_idx = Camp.get_idx(self.camp, year, term)
                stat = get_basic_stat(camp_idx)
                return render_template('%s/old_stat_2.html' % self.camp, stat=stat, year=year, term=term)

        # 엑셀 다운로드
        @self.context.route('/old-excel-down', methods=['GET'])
        @login_required
        @self.hq_permission.require(http_exception=403)
        @self.camp_permission.require(http_exception=403)
        def old_excel_down():
            year = int(request.args.get('year', 0))
            term = int(request.args.get('term', 0))
            name = request.args.get('name', None)
            area = request.args.get('area', None)
            camp = request.args.get('camp', None)
            camptype = request.args.get('camptype', None)
            campcode = request.args.get('campcode', "%s_%d_%d" % (camptype, year, term))

            if year == 0 or term == 0:
                campcode = request.args.get('campcode', None)
                member_list = mongo.get_member_list_with_count(campcode=campcode, name=name, area=area, camp=camp)
                output = xlsx.get_old_document(member_list=member_list, db_type='mongo')
            else:
                area_idx = request.args.get('area_idx', None)
                camp_idx = Camp.get_idx(camptype, year, term)
                member_list = Member.get_old_list(camp_idx=camp_idx, name=name, area_idx=area_idx)
                for member in member_list:
                    count = mongo.db.count({"hp1": member.contact, "name": member.name, "entry": "Y", "fin": {"$ne": "d"}})
                    count += Member.count(name=member.name, contact=member.contact, attend_yn=1, cancel_yn=0)
                    setattr(member, 'campcode', campcode)
                    setattr(member, 'count', count)

                output = xlsx.get_old_document(member_list=member_list, db_type='mysql')

            response = make_response(output.read())
            response.headers["Content-Disposition"] = "attachment; filename=member.xlsx"
            return response

        @self.context.errorhandler(403)
        def forbidden(e):
            flash(u'권한이 없습니다.')
            return redirect(url_for('.home', next=request.url))


class CmcView(MetaView):
    def __init__(self):
        MetaView.__init__(self, 'cmc')
        self.init_home()
        self.init_member_list()

        # 개인 신청 수정
        @self.context.route('/member-edit')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit():
            idx = request.args.get('member_idx', 0)
            session['idx'] = idx
            member = Member.get(idx)
            group_yn = member.group_idx is not None

            from core.forms.cmc import RegistrationForm
            form = RegistrationForm()
            form.set_member_data(member)

            return render_template('%s/form.html' % self.camp, form=form, editmode=True, group_yn=group_yn)

        # **수정필요!!
        # 수정된 신청서 저장
        @self.context.route('/member-edit', methods=['POST'])
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit_proc():
            formData = getIndividualFormData()
            # camp_idx = Camp.get_idx(self.camp)

            idx = session['idx']

            date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
            date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
            td = (date_of_leave - date_of_arrival)

            if td.days < 0:
                flash(u'참석 기간을 잘못 선택하셨습니다.')
                return redirect(url_for('.member_edit', idx=idx))
            else:
                Member.update(idx, **request.form)
                flash(u'신청서 수정이 완료되었습니다.')
                return redirect(url_for('.member', member_idx=idx))


class CbtjView(MetaView):

    def init_home(self):
        # 메인통계
        @self.context.route('/')
        @login_required
        def home():
            camp_idx = getCampIdx('cbtj')
            stat1 = get_basic_stat(camp_idx)

            camp_idx2 = getCampIdx('cbtj2')
            stat2 = get_basic_stat(camp_idx2)

            stat = get_basic_stat(camp_idx, camp_idx2)
            return render_template('%s/home.html' % self.camp, stat1=stat1, stat2=stat2, stat=stat)

    def init_member_list(self):
        # 신청자 목록
        @self.context.route('/list')
        @login_required
        def member_list():
            camp = request.args.get('camp', None)
            group_idx = request.args.get('group_idx', None)
            page = int(request.args.get('page', 1))
            group = Group.get(group_idx) if group_idx is not None else None

            if camp is None or camp == 'None':
                member_list = Member.get_list(Camp.get_idx('cbtj'), **request.args.to_dict())
                member_list.extend(Member.get_list(Camp.get_idx('cbtj2'), **request.args.to_dict()))
                count = Member.count(Camp.get_idx('cbtj'), **request.args.to_dict()) + Member.count(Camp.get_idx('cbtj2'), **request.args.to_dict())
            else:
                camp_idx = Camp.get_idx(camp)
                member_list = Member.get_list(camp_idx, **request.args.to_dict())
                count = Member.count(camp_idx, **request.args.to_dict())
            return render_template(
                '%s/list.html' % self.camp, members=member_list, group=group, count=count-(page-1)*50, nav=range(1, int(count/50)+2)
            )

    def __init__(self):
        MetaView.__init__(self, 'cbtj')
        self.init_home()
        self.init_member_list()

        # 개인 신청 수정
        @self.context.route('/member-edit')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit():
            idx = request.args.get('member_idx', 0)
            session['idx'] = idx
            member = Member.get(idx)
            group_yn = member.group_idx is not None
            camp = request.args.get('camp')

            from core.forms.cbtj import RegForm1, RegForm2
            form = RegForm1() if camp == 'cbtj' else RegForm2()
            form.set_member_data(member)

            return render_template('%s/form.html' % self.camp, form=form, editmode=True, group_yn=group_yn)

        # **수정필요!!
        # 수정된 신청서 저장
        @self.context.route('/member-edit', methods=['POST'])
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit_proc():
            # camp_idx = Camp.get_idx(self.camp)

            idx = session['idx']

            date_of_arrival = datetime.datetime.strptime(request.form.get('date_of_arrival'), '%Y-%m-%d')
            date_of_leave = datetime.datetime.strptime(request.form.get('date_of_leave'), '%Y-%m-%d')
            td = (date_of_leave - date_of_arrival)

            if td.days < 0:
                flash(u'참석 기간을 잘못 선택하셨습니다.')
                return redirect(url_for('.member_edit', member_idx=idx))
            else:
                Member.update(idx, **request.form)
                flash(u'신청서 수정이 완료되었습니다.')
                return redirect(url_for('.member', member_idx=idx))


class KidsView(MetaView):
    def __init__(self):
        MetaView.__init__(self, 'kids')
        self.init_home()
        self.init_member_list()


class YouthView(MetaView):
    def __init__(self):
        MetaView.__init__(self, 'youth')
        self.init_home()
        self.init_member_list()

        # 홍보물 신청 목록
        @self.context.route('/promotion-list')
        @login_required
        def promotion_list():
            camp_idx = Camp.get_idx('youth')
            promotion_list = Promotion.get_list(camp_idx)
            return render_template('%s/promotion_list.html' % self.camp, promotions=promotion_list)


class WsView(MetaView):
    def __init__(self):
        MetaView.__init__(self, 'ws')
        self.init_home()
        self.init_member_list()

        # 개인 신청 수정
        @self.context.route('/member-edit')
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit():
            idx = request.args.get('member_idx', 0)
            session['idx'] = idx
            # member = getIndividualData(idx)
            member = Member.get(idx)
            campidx = Camp.get_idx('ws')
            area_list = getAreaList('ws')  # form에 들어갈 지부 목록
            date_select_list = getDateSelectList()  # form 생년월일에 들어갈 날자 목록

            group_yn = member.group is not None

            return render_template(
                'ws/member_edit.html', camp='ws', campidx=campidx, member=member, membership=member.get_membership_data(),
                area_list=area_list, date_select_list=date_select_list, group_yn=group_yn
            )

        # 수정된 신청서 저장
        @self.context.route('/member-edit', methods=['POST'])
        @login_required
        @self.camp_permission.require(http_exception=403)
        def member_edit_proc():
            idx = session['idx']

            date_of_arrival = datetime.datetime.strptime(request.form.get('date_of_arrival'), '%Y-%m-%d')
            date_of_leave = datetime.datetime.strptime(request.form.get('date_of_leave'), '%Y-%m-%d')
            td = (date_of_leave - date_of_arrival)

            if td.days < 0:
                flash(u'참석 기간을 잘못 선택하셨습니다.')
                return redirect(url_for('.member_edit', member_idx=idx))
            else:
                Member.update(idx, **request.form)
                flash(u'신청서 수정이 완료되었습니다.')
                return redirect(url_for('.member', member_idx=idx))
            # formData = getIndividualFormData()
            # camp_idx = Camp.get_idx('ws')

            # idx = session['idx']

            # date_of_arrival = datetime.datetime.strptime(formData['date_of_arrival'], '%Y-%m-%d')
            # date_of_leave = datetime.datetime.strptime(formData['date_of_leave'], '%Y-%m-%d')
            # td = date_of_leave - date_of_arrival
            # if td.days < 0:
            #    flash(u'참석 기간을 잘못 선택하셨습니다.')
            #    return redirect(url_for('.member_edit', idx=idx))
            # else:
            #    editIndividual(camp_idx, idx, formData)
            #    flash(u'신청서 수정이 완료되었습니다.')
            #    return redirect(url_for('.member', member_idx=idx))
