# -*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, desc, or_, func
from sqlalchemy.orm import relationship, backref
from core.database import db
from core.functions import getAttendArray
import datetime
import hashlib


# 지부
class Area(db.Base):
    __tablename__ = "area"

    idx = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    camp = Column(String)

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls, camp):
        result = []
        if camp == '*':
            area_list = db.db_session.query(cls).order_by(cls.type, cls.name).all()
            return area_list
        else:
            area_list = db.db_session.query(cls).filter(or_(cls.camp == '*', cls.camp.like("%"+camp+"%"))).order_by(cls.type, cls.name).all()

            for area in area_list:
                result.append((area.idx, area.name))

            return result

    # 주어진 area_idx에 해당하는 area_name을 반환하는 함수
    @classmethod
    def get_name(cls, idx):
        area = db.db_session.query(cls).filter(cls.idx == idx).one()
        return area.name

    @classmethod
    def insert(cls, name, type, camp):
        area = cls()
        area.name = name
        area.type = type
        area.camp = camp

        db.db_session.add(area)
        db.db_session.commit()
        pass

    @classmethod
    def update(cls, idx, name, type, camp):
        area = cls.get(idx)
        if area is None:
            area = cls()
            area.name = name
            area.type = type
            area.camp = camp
            db.db_session.add(area)
        else:
            area.name = name
            area.type = type
            area.camp = camp

        db.db_session.commit()


# 캠프
class Camp(db.Base):
    __tablename__ = 'camp'

    idx = Column(Integer, primary_key=True)
    code = Column(String)
    year = Column(Integer)
    term = Column(Integer)
    startday = Column(Date)
    campday = Column(Integer)
    name = Column(String)

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    # camp_idx 반환, year와 term을 파라메터로 넘겨줄 경우 해당 연도와 학기의 camp_idx를 반환해주고
    # year와 term파라메터가 없을 경우 GlobalOptions에 등록되어있는 year와 term을 현재 활성화되어있는 캠프의 camp_idx를 반환해줌.
    @classmethod
    def get_idx(cls, code, year=None, term=None):
        if year is None or year == 0:
            year = GlobalOptions.get_year()
        if term is None or term == 0:
            term = GlobalOptions.get_term()
        return db.db_session.query(cls).filter(cls.code == code, cls.year == year, cls.term == term).one().idx

    # 캠프가 진행되는 날자를 리스트 형태로 반환해주는 함수
    @classmethod
    def get_date_list(cls, camp_idx):
        camp = db.db_session.query(cls).filter(cls.idx == camp_idx).one()
        startday = camp.startday
        campday = camp.campday

        datelist = []
        for i in range(campday):
            date = startday + datetime.timedelta(days=(i))
            datelist.append((date, date))

        return datelist


# 개인 신청서 / 단체 멤버 신청서
class Member(db.Base):
    __tablename__ = 'member'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer, ForeignKey('camp.idx'))
    userid = Column(String)
    pwd = Column(String)
    name = Column(String)
    area_idx = Column(Integer, ForeignKey('area.idx'))
    contact = Column(String)
    church = Column(String)
    birth = Column(String)
    sex = Column(String)
    bus_yn = Column(Integer)
    mit_yn = Column(Integer)
    attend_yn = Column(Integer)
    newcomer_yn = Column(Integer)
    persontype = Column(String)
    fullcamp_yn = Column(Integer)
    date_of_arrival = Column(Date)
    date_of_leave = Column(Date)
    language = Column(String)
    group_idx = Column(Integer, ForeignKey('group.idx'))
    regdate = Column(DateTime)
    canceldate = Column(DateTime)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String)
    memo = Column(String)
    room_idx = Column(Integer, ForeignKey('room.idx'))
    attend1 = Column(Integer)
    attend2 = Column(Integer)
    attend3 = Column(Integer)
    attend4 = Column(Integer)

    membership = relationship("Membership", order_by="Membership.key", backref=backref("membership_member"))
    payment = relationship("Payment", uselist=False, backref=backref("payment_member"))
    group = relationship("Group", backref=backref("group_members", lazy='dynamic'))
    area = relationship("Area", backref=backref("area_member", lazy='dynamic'))
    camp = relationship("Camp", backref=backref("camp_member", lazy='dynamic'))
    room = relationship("Room", backref=backref("room_member", lazy='dynamic'))

    def get_id(self):
        return self.idx

    @classmethod
    def get_idx(cls, camp_idx, userid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).first().idx

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).one()

    @classmethod
    def find(cls, camp_idx, userid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).first()

    @classmethod
    def get_filtered_result(cls, result, orderby=None, isnull=None, **kwargs):
        membership_keys = ['training', 'campus', 'job']
        payment_keys = ['complete']
        for key, value in kwargs.iteritems():
            if value is not None and value != '':
                value = [value] if type(value) is not list else value
                if key in membership_keys:
                    filter_list = [cls.membership.any(value=v) for v in value]
                elif key in payment_keys:
                    filter_list = [getattr(Payment, key) == v for v in value]
                elif key == 'name':
                    filter_list = [getattr(cls, key).like('%' + v + '%') for v in value]
                else:
                    filter_list = [getattr(cls, key) == v for v in value]
                result = result.filter(or_(*filter_list))

        if isnull is not None:
            isnull = [isnull] if type(isnull) is not list else isnull
            for i in isnull:
                attr = getattr(cls, i)
                result = result.filter(or_(attr.is_(None), attr == ''))

        if orderby is None:
            result = result.order_by(desc(cls.idx))
        else:
            orderby = [orderby] if type(orderby) is not list else orderby
            for o in orderby:
                result = result.order_by(desc(getattr(cls, o)))

        return result

    @classmethod
    def get_list(cls, camp_idx=None, orderby=None, isnull=None, **kwargs):
        result = db.db_session.query(cls)
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]
            result = result.filter(or_(*filter_list))

        page = int(kwargs.pop('page', 0))
        kwargs.pop('camp', None)

        result = cls.get_filtered_result(result, orderby=orderby, isnull=isnull, **kwargs)
        return result.all() if page == 0 else result.limit(50).offset((page-1)*50).all()

    # 특정 camp_idx에 해당하는 member의 수를 반환하는 함수. 필터 조건을 파라메터로 넘길 수 있음. (예: persontype=u'청년')
    @classmethod
    def count(cls, camp_idx=None, isnull=None, **kwargs):
        result = db.db_session.query(cls)
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]
            result = result.filter(or_(*filter_list))

        kwargs.pop('page', None)
        kwargs.pop('camp', None)

        result = cls.get_filtered_result(result, isnull=isnull, **kwargs)

        return result.count()

    @classmethod
    def get_old_list(cls, camp_idx, offset=None, **kwargs):
        result = db.db_session.query(cls).filter(cls.camp_idx == camp_idx)
        for key, value in kwargs.iteritems():
            if value is not None and value != '':
                attr = getattr(cls, key)
                result = result.filter(attr == value)

        result = result.order_by(desc(cls.idx))

        member_list = result.limit(50).offset(offset).all() if offset is not None else result.all()
        return member_list

    # 멤버 정보 수정
    @classmethod
    def update(cls, member_idx, camp_idx=None, formData=None, membership_data_list=None, **kwargs):
        member = cls.get(member_idx)
        if member is not None:
            if formData is not None:
                attend = getAttendArray(camp_idx, formData)
                member.attend1 = attend[0]
                member.attend2 = attend[1]
                member.attend3 = attend[2]
                member.attend4 = attend[3]

                form_keys = [
                    'name', 'area_idx', 'church', 'birth', 'sex', 'bus_yn',
                    'mit_yn', 'newcomer_yn', 'persontype', 'fullcamp_yn', 'date_of_arrival',
                    'date_of_leave', 'language', 'memo'
                ]

                for key in form_keys:
                    if key in formData:
                        setattr(member, key, formData[key])

                # pwd필드의 값이 없거나 공백일 경우 pwd값을 변경하지 않음.
                if 'pwd' in formData and formData['pwd'] is not None and formData['pwd'] != '':
                    member.pwd = formData['pwd']

                member.contact = formData['hp'] + '-' + formData['hp2'] + '-' + formData['hp3']

                if membership_data_list is not None:
                    db.db_session.query(Membership).filter(Membership.member_idx == member_idx).delete()

                    for membership_data in membership_data_list:
                        membership = Membership()
                        membership.camp_idx = camp_idx
                        membership.member_idx = member_idx
                        membership.key = membership_data['key']
                        membership.value = membership_data['value']
                        db.db_session.add(membership)
            else:
                if 'date_of_arrival' in kwargs and 'date_of_leave' in kwargs:
                    attend = member.get_attend_array(kwargs.get('date_of_arrival')[0], kwargs.get('date_of_leave')[0])
                    member.attend1 = attend[0]
                    member.attend2 = attend[1]
                    member.attend3 = attend[2]
                    member.attend4 = attend[3]

            membership_keys = ['job', 'campus', 'major', 'sm_yn', 'training', 'route', 'stafftype', 'pname', 'sch1', 'sch2']
            membership_list = []
            for key, value in kwargs.iteritems():
                value = value[0] if type(value) is list and len(value) == 1 else value
                # if value is not None and value != '':
                if key == 'pwd':
                    if value is not None and value != '':
                        setattr(member, key, hashlib.sha224(value).hexdigest())
                elif key == 'hp2' or key == 'hp3':
                    pass
                elif key == 'hp':
                    setattr(member, 'contact', '-'.join(kwargs.get('hp') + kwargs.get('hp2') + kwargs.get('hp3')))
                elif key in membership_keys:
                    if key == 'training' or key == 'route':
                        if type(value) is list:
                            for v in value:
                                membership_list.append((key, v))
                        else:
                            membership_list.append((key, value))
                    else:
                        membership_list.append((key, value))
                else:
                    setattr(member, key, value)

            if len(membership_list) > 0:
                db.db_session.query(Membership).filter(Membership.member_idx == member_idx).delete()
                for key, value in membership_list:
                    membership = Membership()
                    membership.camp_idx = member.camp_idx
                    membership.member_idx = member.idx
                    membership.key = key
                    membership.value = value
                    db.db_session.add(membership)

            db.db_session.commit()

    # 멤버 추가 함수
    @classmethod
    def insert(cls, camp_idx, formData, group_idx, membership_data_list):
        member = cls()

        member.camp_idx = camp_idx
        member.group_idx = group_idx
        member.regdate = datetime.datetime.today()
        member.cancel_yn = 0
        member.attend_yn = 0

        attend = getAttendArray(camp_idx, formData)
        member.attend1 = attend[0]
        member.attend2 = attend[1]
        member.attend3 = attend[2]
        member.attend4 = attend[3]

        form_keys = [
            'userid', 'pwd', 'name', 'area_idx', 'church', 'birth', 'sex', 'bus_yn',
            'mit_yn', 'newcomer_yn', 'persontype', 'fullcamp_yn', 'date_of_arrival',
            'date_of_leave', 'language', 'memo'
        ]

        for key in form_keys:
            if key in formData:
                setattr(member, key, formData[key])

        member.contact = formData['hp'] + '-' + formData['hp2'] + '-' + formData['hp3']

        db.db_session.add(member)
        db.db_session.commit()

        member_idx = member.idx

        for membership_data in membership_data_list:
            membership = Membership()
            membership.camp_idx = camp_idx
            membership.member_idx = member_idx
            membership.key = membership_data['key']
            membership.value = membership_data['value']
            db.db_session.add(membership)

        db.db_session.commit()
        return member_idx

    @classmethod
    def check_userid(cls, camp_idx, userid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).count()

    @classmethod
    def login_check(cls, camp_idx, userid, pwd):
        count = db.db_session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.userid == userid,
            cls.pwd == hashlib.sha224(pwd).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False

    @classmethod
    def cancel(cls, idx, reason):
        member = cls.get(idx)
        member.cancel_yn = 1
        member.cancel_reason = reason
        member.canceldate = datetime.datetime.today()
        db.db_session.commit()

    @classmethod
    def delete(cls, idx):
        db.db_session.query(Payment).filter(Payment.member_idx == idx).delete()
        db.db_session.query(Membership).filter(Membership.member_idx == idx).delete()
        db.db_session.query(cls).filter(cls.idx == idx).delete()

    def get_membership_data(self):
        membership_data = dict()

        for t in self.membership:
            if t.key == 'training' or t.key == 'route':
                if t.key in membership_data:
                    membership_data[t.key].append(t.value)
                else:
                    membership_data[t.key] = [t.value]
            else:
                membership_data[t.key] = t.value

        return membership_data

    def get_attend_array(self, date_of_arrival, date_of_leave):
        camp = Camp.get(self.camp_idx)

        date_of_arrival = datetime.datetime.strptime(date_of_arrival, '%Y-%m-%d').date()
        date_of_leave = datetime.datetime.strptime(date_of_leave, '%Y-%m-%d').date()

        i = (date_of_arrival-camp.startday).days
        interval = range(0, (date_of_leave - date_of_arrival).days+1)
        attend = [0, 0, 0, 0]
        for j in interval:
            attend[i+j] = 1

        return attend

    @classmethod
    def get_attend_stat(cls, camp_idx):
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        count = db.db_session.query(
            func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)
        ).filter(*filter_list).filter(cls.cancel_yn == 0).one()
        r_count = db.db_session.query(
            func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)
        ).filter(*filter_list).filter(cls.cancel_yn == 0).filter(cls.payment != None).one()
        a_count = db.db_session.query(func.sum(
            cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)
        ).filter(*filter_list).filter(cls.attend_yn == 1).one()

        stat = [
            {'cnt': count[0], 'r_cnt': r_count[0] if r_count[0] is not None else 0, 'a_cnt': a_count[0] if a_count[0] is not None else 0},
            {'cnt': count[1], 'r_cnt': r_count[1] if r_count[1] is not None else 0, 'a_cnt': a_count[1] if a_count[1] is not None else 0},
            {'cnt': count[2], 'r_cnt': r_count[2] if r_count[2] is not None else 0, 'a_cnt': a_count[2] if a_count[2] is not None else 0},
            {'cnt': count[3], 'r_cnt': r_count[3] if r_count[3] is not None else 0, 'a_cnt': a_count[3] if a_count[3] is not None else 0},
        ]

        return stat

    @classmethod
    def get_partial_stat(cls, camp_idx):
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        stmt = db.db_session.query((cls.attend1 + cls.attend2 + cls.attend3 + cls.attend4).label('partial')).filter(or_(*filter_list)).subquery()
        count = db.db_session.query(stmt, func.count('partial')).group_by('partial').all()
        return count

    @classmethod
    def fix_attend_error(cls, camp_idx):
        member_list = cls.get_list(camp_idx)
        for member in member_list:
            if member.fullcamp_yn == 1:
                date_list = Camp.get_date_list(member.camp_idx)
                member.date_of_arrival = date_list[0][0]
                member.date_of_leave = date_list[-1][0]

            if member.cancel_yn == 1:
                member.attend1 = 0
                member.attend2 = 0
                member.attend3 = 0
                member.attend4 = 0
            else:
                # attend = member.get_attend_array(member.date_of_arrival, member.date_of_leave)
                camp = Camp.get(member.camp_idx)
                if camp.code == 'ws' or camp.code == 'youth' or camp.code == 'kids' or camp.code == 'cbtj2':
                    if member.date_of_arrival.year == 2015:
                        member.date_of_arrival = member.date_of_arrival.replace(year=2016)

                    if member.date_of_leave.year == 2015:
                        member.date_of_leave = member.date_of_leave.replace(year=2016)

                i = (member.date_of_arrival-camp.startday).days
                interval = range(0, (member.date_of_leave - member.date_of_arrival).days+1)
                attend = [0, 0, 0, 0]
                for j in interval:
                    attend[i+j] = 1

                member.attend1 = attend[0]
                member.attend2 = attend[1]
                member.attend3 = attend[2]
                member.attend4 = attend[3]

            db.commit()


# 세대별 기타 정보
class Membership(db.Base):
    __tablename__ = 'membership'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    member_idx = Column(Integer, ForeignKey('member.idx'))
    key = Column(String)
    value = Column(String)

    member = relationship("Member", backref='member_memberships')

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls, member_idx):
        return db.db_session.query(cls).filter(cls.member_idx == member_idx).first()


# 입금 정보
class Payment(db.Base):
    __tablename__ = 'payment'

    idx = Column(Integer, primary_key=True)
    member_idx = Column(Integer, ForeignKey('member.idx'))
    amount = Column(Integer)
    complete = Column(Integer)
    claim = Column(String)
    staff_name = Column(String)
    paydate = Column(Date)
    code = Column(String)

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, member_idx):
        return db.db_session.query(cls).filter(cls.member_idx == member_idx).first()

    @classmethod
    def save(cls, member_idx, amount, complete, claim, staff_name, paydate=None):
        if paydate is None or paydate == '':
            paydate = "%s" % datetime.datetime.today().date()

        payment = cls.find(member_idx)
        if payment is None:
            payment = cls()
            payment.member_idx = member_idx
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.paydate = paydate
            payment.staff_name = staff_name
            db.db_session.add(payment)
        else:
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.paydate = paydate
            payment.staff_name = staff_name

        db.db_session.commit()

    @classmethod
    def delete(cls, member_idx):
        db.db_session.query(cls).filter(cls.member_idx == member_idx).delete()
        db.db_session.commit()


# 단체
class Group(db.Base):
    __tablename__ = 'group'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    name = Column(String)
    groupid = Column(String)
    pwd = Column(String)
    leadername = Column(String)
    leaderjob = Column(String)
    leadercontact = Column(String)
    area_idx = Column(Integer, ForeignKey('area.idx'))
    mem_num = Column(Integer)
    grouptype = Column(String)
    regdate = Column(DateTime)
    canceldate = Column(DateTime)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String)
    memo = Column(String)

    member = relationship("Member", order_by="Member.idx", backref="member_group")
    area = relationship("Area", backref=backref("area_group", lazy='dynamic'))

    def get_id(self):
        return self.idx

    @classmethod
    def get_idx(cls, camp_idx, groupid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.groupid == groupid).one().idx

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, camp_idx, groupid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.groupid == groupid).first()

    @classmethod
    def get_list(cls, camp_idx):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.cancel_yn == 0).all()

    @classmethod
    def check_groupid(cls, camp_idx, groupid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.groupid == groupid).count()

    @classmethod
    def login_check(cls, camp_idx, groupid, pwd):
        count = db.db_session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.groupid == groupid,
            cls.pwd == hashlib.sha224(pwd).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False

    @classmethod
    def inc_mem_num(cls, idx):
        group = db.db_session.query(cls).filter(cls.idx == idx).one()
        group.mem_num += 1
        db.db_session.commit()

    @classmethod
    def dec_mem_num(cls, idx):
        group = db.db_session.query(cls).filter(cls.idx == idx).one()
        group.mem_num -= 1
        if group.mem_num < 0:
            group.mem_num = 0
        db.db_session.commit()

    @classmethod
    def insert(cls, camp_idx, formData):
        group = cls()
        group.camp_idx = camp_idx
        group.name = formData['name']
        group.groupid = formData['groupid']
        group.pwd = formData['pwd']
        group.leadername = formData['leadername']
        group.leadercontact = formData['hp'] + '-' + formData['hp2'] + '-' + formData['hp3']
        group.leaderjob = formData['leaderjob']
        group.area_idx = formData['area_idx']
        group.mem_num = 0
        group.grouptype = formData['grouptype'] if 'grouptype' in formData else None
        group.regdate = datetime.datetime.today()
        group.canceldate = None
        group.cancel_yn = 0
        group.cancel_reason = None
        group.memo = formData['memo']

        db.db_session.add(group)
        db.db_session.commit()
        return group.idx

    @classmethod
    def update(cls, idx, formData=None, **kwargs):
        group = cls.get(idx)
        if group is not None:
            if formData is not None:
                form_keys = ['name', 'leadername', 'leaderjob', 'area_idx', 'memo']

                for key in form_keys:
                    setattr(group, key, formData[key] if key in formData else None)

                group.leadercontact = formData['hp'] + '-' + formData['hp2'] + '-' + formData['hp3']
                if 'pwd' in formData and formData['pwd'] is not None and formData['pwd'] != '':
                    group.pwd = formData['pwd']

            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    setattr(group, key, value)

        db.db_session.commit()

    @classmethod
    def cancel(cls, idx, reason):
        group = cls.get(idx)
        group.cancel_yn = 1
        group.cancel_reason = reason
        group.canceldate = datetime.datetime.today()

        member_list = Member.get_list(group_idx=idx)
        for member in member_list:
            if member.cancel_yn == 0:
                member.cancel_yn = 1
                member.cancel_reason = reason
                member.canceldate = datetime.datetime.today()
        db.db_session.commit()


# 청소년 홍보물
class Promotion(db.Base):
    __tablename__ = 'promotion'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    church_name = Column(String)
    name = Column(String)
    address = Column(String)
    contact = Column(String)
    memo = Column(String)

    def __init__(self, camp_idx, church_name, name, address, contact, memo, idx=None):
        self.idx = idx
        self.camp_idx = camp_idx
        self.church_name = church_name
        self.name = name
        self.address = address
        self.contact = contact
        self.memo = memo

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, camp_idx, church_name):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.church_name == church_name).first()

    @classmethod
    def get_list(cls, camp_idx):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx).all()

    @classmethod
    def insert(cls, camp_idx, church_name, name, address, contact, memo):
        promotion = cls(camp_idx, church_name, name, address, contact, memo)
        db.db_session.add(promotion)
        db.db_session.commit()


class GlobalOptions(db.Base):
    __tablename__ = 'global_options'

    key = Column(String, primary_key=True)
    value = Column(String)

    @classmethod
    def get_year(cls):
        return int(db.db_session.query(cls).filter(cls.key == 'current_year').one().value)

    @classmethod
    def get_term(cls):
        return int(db.db_session.query(cls).filter(cls.key == 'current_term').one().value)


class Options(db.Base):
    __tablename__ = 'options'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    key = Column(String)
    value = Column(String)

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).one()

    @classmethod
    def get_value(cls, camp_idx, key):
        return db.db_session.query(cls).filteR(cls.camp_idx == camp_idx, cls.key == key).one().value


class Room(db.Base):
    __tablename__ = 'room'

    idx = Column(Integer, primary_key=True)
    building = Column(String)
    number = Column(String)

    @classmethod
    def get(cls, idx):
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls):
        return db.db_session.query(cls).order_by(cls.building, cls.number).all()

    @classmethod
    def get_stat(cls, camp_idx):
        room_list = cls.get_list()
        stat = dict()
        for room in room_list:
            # stat[room.idx] = Member.count(camp_idx=camp_idx, room_idx=room.idx)
            stat[room.idx] = 0

        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [Member.camp_idx == idx for idx in camp_idx]

        count = db.db_session.query(Member.room_idx, func.count(Member.idx)).filter(or_(*filter_list)).group_by(Member.room_idx)

        for room_idx, cnt in count.all():
            if room_idx is not None:
                stat[room_idx] = cnt

        return stat
