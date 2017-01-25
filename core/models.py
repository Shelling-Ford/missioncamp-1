'''core.models.py
'''
# pylint: disable=R0903,C0301
import datetime
import hashlib
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, or_, func
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from core.database import DB as db


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
    def get_list(cls, camp, use_model=False):
        '''Area.get_list
        '''
        result = []
        if camp == '*':
            area_list = db.session.query(cls).filter(cls.type != 4).order_by(cls.type, cls.name).all()
        else:
            area_list = db.session.query(cls).filter(or_(cls.camp == '*', cls.camp.like("%{}%".format(camp))), cls.type != 4).order_by(cls.type, cls.name).all()

        if use_model:
            return area_list

        for area in area_list:
            result.append((area.idx, area.name))
        return result


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

    # camp_idx 반환, year와 term을 파라메터로 넘겨줄 경우 해당 연도와 학기의 camp_idx를 반환해주고
    # year와 term파라메터가 없을 경우 GlobalOptions에 등록되어있는 year와 term을 현재 활성화되어있는 캠프의 camp_idx를 반환해줌.
    @classmethod
    def get_idx(cls, code, year=None, term=None):
        '''Camp.get_idx
        '''
        if year is None or year == 0:
            year = int(db.session.query(GlobalOptions).filter(GlobalOptions.key == 'current_year').one().value)
        if term is None or term == 0:
            term = int(db.session.query(GlobalOptions).filter(GlobalOptions.key == 'current_term').one().value)
        return db.session.query(cls).filter(cls.code == code, cls.year == year, cls.term == term).one().idx

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

    membership = relationship("Membership", order_by="Membership.key", backref=backref("membership_member"))
    payment = relationship("Payment", uselist=False, backref=backref("payment_member"))
    group = relationship("Group", backref=backref("group_members", lazy='dynamic'))
    area = relationship("Area", backref=backref("area_member", lazy='dynamic'))
    camp = relationship("Camp", backref=backref("camp_member", lazy='dynamic'))
    room = relationship("Room", backref=backref("room_member", lazy='dynamic'))

    def get_id(self):
        return self.idx

    @classmethod
    def check_userid(cls, camp_idx, userid):
        '''
        아이디 중복체크
        '''
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).count()

    @classmethod
    def login_check(cls, camp_idx, userid, pwd):
        '''
        로그인 체크
        '''
        count = db.session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.userid == userid,
            cls.pwd == hashlib.sha224(pwd.encode('utf-8')).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False

    def get_membership_data(self):
        '''
        가변필드 받아오기
        '''
        membership_data = dict()

        for feild in self.membership:
            if feild.key == 'training' or feild.key == 'route':
                if feild.key in membership_data:
                    membership_data[feild.key].append(feild.value)
                else:
                    membership_data[feild.key] = [feild.value]
            else:
                membership_data[feild.key] = feild.value

        return membership_data

    def get_attend_array(self):
        '''
        참석일수 관련 배열 가져오기
        '''
        camp = db.session.query(Camp).filter(Camp.idx == self.camp_idx).one()

        attend = [0, 0, 0, 0]
        if self.date_of_arrival is not None and self.date_of_leave is not None:
            if isinstance(self.date_of_arrival, str):
                self.date_of_arrival = datetime.datetime.strptime(self.date_of_arrival, '%Y-%m-%d').date()
            if isinstance(self.date_of_leave, str):
                self.date_of_leave = datetime.datetime.strptime(self.date_of_leave, '%Y-%m-%d').date()

            i = (self.date_of_arrival - camp.startday).days
            interval = range(0, (self.date_of_leave - self.date_of_arrival).days + 1)
            for j in interval:
                attend[i + j] = 1
        return attend

    @classmethod
    def get_attend_stat(cls, camp_idx):
        '''
        참석일수 관련 통계표 가져오기
        '''
        camp_idx = camp_idx if isinstance(camp_idx, list) else [camp_idx]
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        count = db.session.query(func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)).filter(*filter_list).filter(cls.cancel_yn == 0).one()
        r_count = db.session.query(func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)).filter(*filter_list).filter(cls.cancel_yn == 0).filter(cls.payment != None).one()
        a_count = db.session.query(func.sum(cls.attend1), func.sum(cls.attend2), func.sum(cls.attend3), func.sum(cls.attend4)).filter(*filter_list).filter(cls.attend_yn == 1).one()

        stat = [
            {'cnt': count[0], 'r_cnt': r_count[0] if r_count[0] is not None else 0, 'a_cnt': a_count[0] if a_count[0] is not None else 0},
            {'cnt': count[1], 'r_cnt': r_count[1] if r_count[1] is not None else 0, 'a_cnt': a_count[1] if a_count[1] is not None else 0},
            {'cnt': count[2], 'r_cnt': r_count[2] if r_count[2] is not None else 0, 'a_cnt': a_count[2] if a_count[2] is not None else 0},
            {'cnt': count[3], 'r_cnt': r_count[3] if r_count[3] is not None else 0, 'a_cnt': a_count[3] if a_count[3] is not None else 0},
        ]

        return stat

    @classmethod
    def get_partial_stat(cls, camp_idx):
        '''
        참석일수별 통계표 가져오기
        '''
        camp_idx = camp_idx if isinstance(camp_idx, list) else [camp_idx]
        if camp_idx is not None:
            filter_list = [cls.camp_idx == idx for idx in camp_idx]

        stmt = db.session.query((cls.attend1 + cls.attend2 + cls.attend3 + cls.attend4).label('partial')).filter(or_(*filter_list)).subquery()
        count = db.session.query(stmt, func.count('partial')).group_by('partial').all()
        return count

    @classmethod
    def fix_attend_error(cls, camp_idx):
        '''
        참석일수별 배열 재설정
        '''
        member_list = db.session.query(cls).filter(cls.camp_idx == camp_idx).all()
        for member in member_list:
            camp = db.session.query(Camp).filter(Camp.idx == camp_idx).one()

            if member.cancel_yn == 1:
                member.attend1, member.attend2, member.attend3, member.attend4 = (0, 0, 0, 0)
            else:
                if member.fullcamp_yn == 1:
                    date_list = Camp.get_date_list(member.camp_idx)
                    member.date_of_arrival = date_list[0][0]
                    member.date_of_leave = date_list[-1][0]

                    if camp.campday == 4:
                        member.attend1, member.attend2, member.attend3, member.attend4 = (1, 1, 1, 1)
                    else:
                        member.attend1, member.attend2, member.attend3, member.attend4 = (1, 1, 1, 0)
                else:
                    attend = member.get_attend_array()
                    member.attend1, member.attend2, member.attend3, member.attend4 = attend
        db.session.commit()


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
    # member = relationship("Member", backref='member_memberships')


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

    @classmethod
    def check_groupid(cls, camp_idx, groupid):
        '''
        아이디 중복체크
        '''
        return db.session.query(cls).filter(cls.camp_idx == camp_idx, cls.groupid == groupid).count()

    @classmethod
    def login_check(cls, camp_idx, groupid, pwd):
        '''
        로그인 체크
        '''
        count = db.session.query(cls).filter(
            cls.camp_idx == camp_idx, cls.groupid == groupid,
            cls.pwd == hashlib.sha224(pwd.encode('utf-8')).hexdigest(),
            cls.cancel_yn == 0
        ).count()
        return True if count > 0 else False


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


class GlobalOptions(db.base):
    ''' 옵션
    '''
    __tablename__ = 'global_options'

    key = Column(String(45), primary_key=True)
    value = Column(String(200))


class Room(db.base):
    ''' 숙소
    '''
    __tablename__ = 'room'

    idx = Column(Integer, primary_key=True)
    building = Column(String(45))
    number = Column(String(45))

    @classmethod
    def get_stat(cls, camp_idx):
        '''
        숙소 통계 가져오기
        '''
        room_list = db.session.query(cls).all()
        stat = dict()
        cnt_stat = dict()
        a_cnt_stat = dict()
        for room in room_list:
            cnt_stat[room.idx] = 0
            a_cnt_stat[room.idx] = 0

        camp_idx = camp_idx if isinstance(camp_idx, list) else [camp_idx]
        if camp_idx is not None:
            filter_list = [Member.camp_idx == idx for idx in camp_idx]

        count = db.session.query(Member.room_idx, func.count(Member.idx), func.sum(Member.attend_yn)).filter(or_(*filter_list), Member.cancel_yn == 0).group_by(Member.room_idx)

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
    def init(cls, camp_idx):
        '''
        모든 숙소 0으로 초기화
        '''
        room_list = db.session.query(Room).all()
        for room in room_list:
            roomsetting = cls()
            roomsetting.camp_idx = camp_idx
            roomsetting.room_idx = room.idx
            roomsetting.cap = 0
            roomsetting.memo = ''
            db.session.add(roomsetting)
        db.session.commit()
