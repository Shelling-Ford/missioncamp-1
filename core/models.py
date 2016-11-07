'''core.models.py
'''
import datetime
import hashlib
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, or_, func
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from core.database import DB as db

# 지부
class Area(db.base):
    ''' 지부
    '''
    __tablename__ = "area"

    idx = Column(Integer, primary_key=True)
    name = Column(String(45))
    type = Column(String(45))
    camp = Column(String(45))
    chaptercode = Column(String(10))

    @classmethod
    def get(cls, idx):
        '''Area.get
        '''
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls, camp):
        '''Area.get_list
        '''
        result = []
        if camp == '*':
            area_list = db.session.query(cls).filter(cls.type != 4)\
            .order_by(cls.type, cls.name).all()
        else:
            area_list = db.session.query(cls).filter(or_(cls.camp == '*', \
            cls.camp.like("%" + camp + "%")), cls.type != 4).order_by(cls.type, \
            cls.name).all()

        for area in area_list:
            result.append((area.idx, area.name))
        return result

    # 주어진 area_idx에 해당하는 area_name을 반환하는 함수
    @classmethod
    def get_name(cls, idx):
        '''Area.get_name
        '''
        area = db.session.query(cls).filter(cls.idx == idx).one()
        return area.name

    @classmethod
    def get_idx(cls, chaptercode):
        '''Area.get_idx
        '''
        area = db.session.query(cls).filter(cls.chaptercode == chaptercode).one()
        return area.idx


# 캠프
class Camp(db.base):
    ''' 캠프
    '''
    __tablename__ = 'camp'

    idx = Column(Integer, primary_key=True)
    code = Column(String(45))
    year = Column(Integer)
    term = Column(Integer)
    startday = Column(Date)
    campday = Column(Integer)
    name = Column(String(45))

    @classmethod
    def get(cls, idx):
        '''Camp.get
        '''
        return db.session.query(cls).filter(cls.idx == idx).first()

    # camp_idx 반환, year와 term을 파라메터로 넘겨줄 경우 해당 연도와 학기의 camp_idx를 반환해주고
    # year와 term파라메터가 없을 경우 GlobalOptions에 등록되어있는 year와 term을 현재 활성화되어있는 캠프의 camp_idx를 반환해줌.
    @classmethod
    def get_idx(cls, code, year=None, term=None):
        '''Camp.get_idx
        '''
        if year is None or year == 0:
            year = GlobalOptions.get_year()
        if term is None or term == 0:
            term = GlobalOptions.get_term()
        return db.session.query(cls).filter(cls.code == code, cls.year == year, \
        cls.term == term).one().idx

    # 캠프가 진행되는 날자를 리스트 형태로 반환해주는 함수
    @classmethod
    def get_date_list(cls, camp_idx):
        '''Camp.get_date_list
        '''
        camp = db.session.query(cls).filter(cls.idx == camp_idx).one()
        startday = camp.startday
        campday = camp.campday

        datelist = []
        for i in range(campday):
            date = startday + datetime.timedelta(days=(i))
            datelist.append((date, date))

        return datelist


# 개인 신청서 / 단체 멤버 신청서
class Member(db.base, UserMixin):
    ''' 멤버
    '''
    __tablename__ = 'member'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer, ForeignKey('camp.idx'))
    userid = Column(String(100))
    pwd = Column(String(100))
    name = Column(String(45))
    area_idx = Column(Integer, ForeignKey('area.idx'))
    contact = Column(String(45))
    church = Column(String(45))
    birth = Column(String(45))
    sex = Column(String(1))
    bus_yn = Column(Integer)
    mit_yn = Column(Integer)
    attend_yn = Column(Integer)
    newcomer_yn = Column(Integer)
    persontype = Column(String(45))
    fullcamp_yn = Column(Integer)
    date_of_arrival = Column(Date)
    date_of_leave = Column(Date)
    language = Column(String(45))
    group_idx = Column(Integer, ForeignKey('group.idx'))
    regdate = Column(DateTime)
    canceldate = Column(DateTime)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String(1000))
    memo = Column(String(1000))
    room_idx = Column(Integer, ForeignKey('room.idx'))
    smallgroup_num = Column(Integer)
    attend1 = Column(Integer)
    attend2 = Column(Integer)
    attend3 = Column(Integer)
    attend4 = Column(Integer)
    attend_time = Column(DateTime)

    membership = relationship("Membership", order_by="Membership.key", \
    backref=backref("membership_member"))
    payment = relationship("Payment", uselist=False, backref=backref("payment_member"))
    group = relationship("Group", backref=backref("group_members", lazy='dynamic'))
    area = relationship("Area", backref=backref("area_member", lazy='dynamic'))
    camp = relationship("Camp", backref=backref("camp_member", lazy='dynamic'))
    room = relationship("Room", backref=backref("room_member", lazy='dynamic'))

    def get_id(self):
        return self.idx

    @classmethod
    def get_idx(cls, camp_idx, userid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.userid == userid).first().idx

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).one()

    @classmethod
    def find(cls, camp_idx, userid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.userid == userid).first()

    @classmethod
    def check_userid(cls, camp_idx, userid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).count()

    @classmethod
    def login_check(cls, camp_idx, userid, pwd):
        count = db.session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.userid == userid,
            cls.pwd == hashlib.sha224(pwd.encode('utf-8')).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False

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

        i = (date_of_arrival - camp.startday).days
        interval = range(0, (date_of_leave - date_of_arrival).days + 1)
        attend = [0, 0, 0, 0]
        for j in interval:
            attend[i + j] = 1

        return attend

    @classmethod
    def get_attend_stat(cls, camp_idx):
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        count = db.session.query(
            func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), \
            func.sum(cls.attend4)
        ).filter(*filter_list).filter(cls.cancel_yn == 0).one()
        r_count = db.session.query(
            func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), \
            func.sum(cls.attend4)
        ).filter(*filter_list).filter(cls.cancel_yn == 0).filter(cls.payment != \
        None).one()
        a_count = db.session.query(func.sum(cls.attend1), func.sum(cls.attend2), \
        func.sum(cls.attend3), func.sum(cls.attend4)).filter(*filter_list)\
        .filter(cls.attend_yn == 1).one()

        stat = [
            {'cnt': count[0], 'r_cnt': r_count[0] if r_count[0] is not None \
        else 0, 'a_cnt': a_count[0] if a_count[0] is not None else 0},
            {'cnt': count[1], 'r_cnt': r_count[1] if r_count[1] is not None \
        else 0, 'a_cnt': a_count[1] if a_count[1] is not None else 0},
            {'cnt': count[2], 'r_cnt': r_count[2] if r_count[2] is not None \
        else 0, 'a_cnt': a_count[2] if a_count[2] is not None else 0},
            {'cnt': count[3], 'r_cnt': r_count[3] if r_count[3] is not None \
        else 0, 'a_cnt': a_count[3] if a_count[3] is not None else 0},
        ]

        return stat

    @classmethod
    def get_partial_stat(cls, camp_idx):
        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        stmt = db.session.query((cls.attend1 + cls.attend2 + cls.attend3 + \
        cls.attend4).label('partial')).filter(or_(*filter_list)).subquery()
        count = db.session.query(stmt, func.count('partial'))\
        .group_by('partial').all()
        return count

    @classmethod
    def fix_attend_error(cls, camp_idx):
        member_list = db.session.query(cls).filter(cls.camp_idx == camp_idx).all()
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
                camp = Camp.get(member.camp_idx)
                if camp.code == 'ws' or camp.code == 'youth' or camp.code == \
                'kids' or camp.code == 'cbtj2':
                    if member.date_of_arrival.year == 2015:
                        member.date_of_arrival = \
                        member.date_of_arrival.replace(year=2016)

                    if member.date_of_leave.year == 2015:
                        member.date_of_leave = \
                        member.date_of_leave.replace(year=2016)

                i = (member.date_of_arrival-camp.startday).days
                interval = range(0, (member.date_of_leave - \
                member.date_of_arrival).days+1)
                attend = [0, 0, 0, 0]
                for j in interval:
                    attend[i+j] = 1

                if not attend == [member.attend1, member.attend2, member.attend3, \
                member.attend4]:
                    member.attend1 = attend[0]
                    member.attend2 = attend[1]
                    member.attend3 = attend[2]
                    member.attend4 = attend[3]

            db.commit()


# 세대별 기타 정보
class Membership(db.base):
    ''' 멤버 객체의 가변 필드
    '''
    __tablename__ = 'membership'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    member_idx = Column(Integer, ForeignKey('member.idx'))
    key = Column(String(100))
    value = Column(String(100))

    member = relationship("Member", backref='member_memberships')

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls, member_idx):
        return db.session.query(cls).filter(cls.member_idx == member_idx).first()


# 입금 정보
class Payment(db.base):
    ''' 등록비 입금 정보
    '''
    __tablename__ = 'payment'

    idx = Column(Integer, primary_key=True)
    member_idx = Column(Integer, ForeignKey('member.idx'))
    amount = Column(Integer)
    complete = Column(Integer)
    claim = Column(String(500))
    staff_name = Column(String(45))
    paydate = Column(DateTime)
    code = Column(String(45))

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, member_idx):
        return db.session.query(cls).filter(cls.member_idx == member_idx).first()

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
            db.session.add(payment)
        else:
            payment.amount = amount
            payment.complete = complete
            payment.claim = claim
            payment.paydate = paydate
            payment.staff_name = staff_name

        db.session.commit()

    @classmethod
    def delete(cls, member_idx):
        db.session.query(cls).filter(cls.member_idx == member_idx).delete()
        db.session.commit()


# 단체
class Group(db.base):
    ''' 단체
    '''
    __tablename__ = 'group'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    name = Column(String(100))
    groupid = Column(String(45))
    pwd = Column(String(100))
    leadername = Column(String(45))
    leaderjob = Column(String(45))
    leadercontact = Column(String(45))
    area_idx = Column(Integer, ForeignKey('area.idx'))
    mem_num = Column(Integer)
    grouptype = Column(String(45))
    regdate = Column(Date)
    canceldate = Column(Date)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String(1000))
    memo = Column(String(1000))

    member = relationship("Member", order_by="Member.idx", backref="member_group")
    area = relationship("Area", backref=backref("area_group", lazy='dynamic'))

    def get_id(self):
        return self.idx

    @classmethod
    def get_idx(cls, camp_idx, groupid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.groupid == groupid).one().idx

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, camp_idx, groupid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.groupid == groupid).first()

    @classmethod
    def get_list(cls, camp_idx):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.cancel_yn == 0).all()

    @classmethod
    def check_groupid(cls, camp_idx, groupid):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.groupid == groupid).count()

    @classmethod
    def login_check(cls, camp_idx, groupid, pwd):
        count = db.session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.groupid == groupid,
            cls.pwd == hashlib.sha224(pwd.encode('utf-8')).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False

    @classmethod
    def inc_mem_num(cls, idx):
        group = db.session.query(cls).filter(cls.idx == idx).one()
        group.mem_num += 1
        db.session.commit()

    @classmethod
    def dec_mem_num(cls, idx):
        group = db.session.query(cls).filter(cls.idx == idx).one()
        group.mem_num -= 1
        if group.mem_num < 0:
            group.mem_num = 0
        db.session.commit()

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

        db.session.add(group)
        db.session.commit()
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

            kwargs.pop('group_idx', None)
            for key, value in kwargs.items():
                if key == 'pwd':
                    if value is not None and value != '':
                        setattr(group, key, hashlib.sha224(value).hexdigest())
                elif key == 'hp2' or key == 'hp3':
                    pass
                elif key == 'hp':
                    setattr(group, 'leadercontact', '-'.join([kwargs.get('hp'), \
                    kwargs.get('hp2'), kwargs.get('hp3')]))
                else:
                    setattr(group, key, value)

        db.session.commit()

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
        db.session.commit()


# 청소년 홍보물
class Promotion(db.base):
    ''' 홍보물 신청
    '''
    __tablename__ = 'promotion'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    church_name = Column(String(100))
    name = Column(String(100))
    address = Column(String(100))
    contact = Column(String(50))
    created = Column(DateTime)
    memo = Column(String(255))

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
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, camp_idx, church_name):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, \
        cls.church_name == church_name).first()

    @classmethod
    def get_list(cls, camp_idx):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx).all()

    @classmethod
    def insert(cls, camp_idx, church_name, name, address, contact, memo):
        promotion = cls(camp_idx, church_name, name, address, contact, memo)
        promotion.created = datetime.datetime.now()
        db.session.add(promotion)
        db.session.commit()


class GlobalOptions(db.base):
    ''' 옵션
    '''
    __tablename__ = 'global_options'

    key = Column(String(45), primary_key=True)
    value = Column(String(200))

    @classmethod
    def get_year(cls):
        return int(db.session.query(cls).filter(cls.key == 'current_year').one().value)

    @classmethod
    def get_term(cls):
        return int(db.session.query(cls).filter(cls.key == 'current_term').one().value)


class Room(db.base):
    ''' 숙소
    '''
    __tablename__ = 'room'

    idx = Column(Integer, primary_key=True)
    building = Column(String(45))
    number = Column(String(45))

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def get_list(cls):
        return db.session.query(cls).order_by(cls.building, cls.number).all()

    @classmethod
    def get_stat(cls, camp_idx):
        room_list = cls.get_list()
        stat = dict()
        cnt_stat = dict()
        a_cnt_stat = dict()
        for room in room_list:
            cnt_stat[room.idx] = 0
            a_cnt_stat[room.idx] = 0

        camp_idx = [camp_idx] if type(camp_idx) is not list else camp_idx
        if camp_idx is not None:
            filter_list = [Member.camp_idx == idx for idx in camp_idx]

        count = db.session.query(Member.room_idx, func.count(Member.idx), \
        func.sum(Member.attend_yn)).filter(or_(*filter_list), Member.cancel_yn == 0)\
        .group_by(Member.room_idx)

        for room_idx, cnt, a_cnt in count.all():
            if room_idx is not None:
                cnt_stat[room_idx] = cnt
                a_cnt_stat[room_idx] = a_cnt

        stat['cnt'] = cnt_stat
        stat['a_cnt'] = a_cnt_stat
        return stat


class Roomsetting(db.base):
    ''' 숙소 셋팅
    '''
    __tablename__ = 'roomsetting'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer, ForeignKey('camp.idx'))
    room_idx = Column(Integer, ForeignKey('room.idx'))
    cap = Column(Integer)
    memo = Column(String(1000))

    camp = relationship("Camp", backref=backref("camp_roomsetting", lazy='dynamic'))
    room = relationship("Room", backref=backref("room_roomsetting", lazy='dynamic'))

    @classmethod
    def get_list(cls, camp_idx):
        return db.session.query(cls).filter(cls.camp_idx == camp_idx).all()

    @classmethod
    def init(cls, camp_idx):
        room_list = Room.get_list()
        for room in room_list:
            roomsetting = cls()
            roomsetting.camp_idx = camp_idx
            roomsetting.room_idx = room.idx
            roomsetting.cap = 0
            roomsetting.memo = ''
            db.session.add(roomsetting)
        db.session.commit()

    @classmethod
    def get(cls, idx):
        return db.session.query(cls).filter(cls.idx == idx).one()

    def save(self):
        db.session.commit()
