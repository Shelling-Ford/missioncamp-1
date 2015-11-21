#-*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, Date, ForeignKey, desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from core.database import db
import datetime

class Area(db.Base):
    __tablename__ = "area"

    idx = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    camp = Column(String)


class Member(db.Base):
    __tablename__ = 'member'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
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
    regdate = Column(Date)
    canceldate = Column(Date)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String)
    memo = Column(String)
    room_idx = Column(Integer)
    attend1 = Column(Integer)
    attend2 = Column(Integer)
    attend3 = Column(Integer)
    attend4 = Column(Integer)

    membership = relationship("Membership", order_by="Membership.key", backref=backref("membership_member"))
    payment = relationship("Payment", uselist=False, backref=backref("payment_member"))
    group = relationship("Group", backref=backref("group_members", lazy='dynamic'))
    area = relationship("Area", backref=backref("area_member", lazy='dynamic'))

    def __init__(self, camp_idx, userid, pwd, area_idx, **kwargs):
        keys = [
            'idx', 'name', 'contact',
            'church', 'birth', 'sex', 'bus_yn', 'mit_yn', 'attend_yn',
            'newcomer_yn', 'persontype', 'fullcamp_yn', 'date_of_arrival',
            'date_of_leave', 'language', 'group_idx', 'regdate', 'canceldate',
            'cancel_yn', 'cancel_reason', 'memo', 'room_idx', 'attend1',
            'attend2', 'attend3', 'attend4'
        ]

        self.camp_idx = camp_idx
        self.userid = userid
        self.pwd = pwd
        self.area_idx = area_idx

        for key in keys:
            if key in kwargs:
                self[key] = kwargs[key]
            else:
                self[key] = None

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        try:
            return db.db_session.query(cls).filter(cls.idx == idx).one()
        except NoResultFound:
            return None

    @classmethod
    def find(cls, camp_idx, userid):
        try:
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).one()
        except NoResultFound:
            return None

    @classmethod
    def get_list(cls, camp_idx, **kwargs):
        try:
            result = db.db_session.query(cls).join(Area).outerjoin(Group).outerjoin(Payment).filter(cls.camp_idx == camp_idx)
            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    attr = getattr(cls, key)
                    result = result.filter(attr == value)

            return result.order_by(desc(cls.idx)).all()
        except NoResultFound:
            return None

    @classmethod
    def get_old_list(cls, camp_idx, offset=None, **kwargs):
        try:
            result = db.db_session.query(cls).join(Area).outerjoin(Membership).filter(cls.camp_idx == camp_idx)
            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    attr = getattr(cls, key)
                    result = result.filter(attr == value)

            result = result.order_by(desc(cls.idx))

            if offset is not None:
                return result.limit(200).offset(offset).all()
            else:
                return result.all()
        except NoResultFound:
            return None

    @classmethod
    def count(cls, camp_idx, **kwargs):
        try:
            result = db.db_session.query(cls).join(Area).outerjoin(Group).outerjoin(Payment).filter(cls.camp_idx == camp_idx)
            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    attr = getattr(cls, key)
                    result = result.filter(attr == value)

            return result.count()
        except NoResultFound:
            return None

    @classmethod
    def update(cls, member_idx, **kwargs):
        member = cls.get(member_idx)
        if member is not None:
            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    setattr(member, key, value)

        db.db_session.commit()

class Membership(db.Base):
    __tablename__ = 'membership'

    idx = Column(Integer, primary_key=True)
    camp_idx = Column(Integer)
    member_idx = Column(Integer, ForeignKey('member.idx'))
    key = Column(String)
    value = Column(String)

    member = relationship("Member", backref='member_memberships')

    def __init__(self, camp_idx, member_idx, key, value, idx=None):
        self.idx = idx
        self.camp_idx = camp_idx
        self.member_idx = memeber_idx
        self.key = key
        self.value = value

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        try:
            return db.db_session.query(cls).filter(cls.idx == idx).one()
        except NoResultFound:
            return None

    @classmethod
    def get_list(cls, member_idx):
        try:
            return db.db_session.query(cls).filteR(cls.member_idx == member_idx).all()
        except NoResultFound:
            return None

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

    def __init__(self, member_idx, amount, complete, claim, staff_name, paydate, code, idx=None):
        self.idx = idx
        self.member_idx = memeber_idx
        self.amount = amount
        self.complete = complete
        self.claim = claim
        self.staff_name = staff_name
        self.paydate
        self.code = code

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        try:
            return db.db_session.query(cls).filter(cls.idx == idx).one()
        except NoResultFound:
            return None


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
    area_idx = Column(Integer)
    mem_num = Column(Integer)
    grouptype = Column(String)
    regdate = Column(Date)
    canceldate = Column(Date)
    cancel_yn = Column(Integer)
    cancel_reason = Column(String)
    memo = Column(String)

    member = relationship("Member", order_by="Member.idx", backref="member_group")

    def __init__(self, camp_idx, name, groupid, pwd, leadername, leaderjob, leadercontact, area_idx, **kwargs):
        if 'idx' in kwargs:
            self.idx = kwargs['idx']

        self.camp_idx = camp_idx
        self.name = name
        self.groupid = name
        self.pwd = pwd
        self.leadername = leadername
        self.leaderjob = leaderjob
        self.leadercontact = leadercontact
        self.area_idx = area_idx

        if 'mem_num' in kwargs:
            self.mem_num = kwargs['mem_num']
        else:
            self.mem_num = 0

        if 'grouptype' in kwargs:
            self.grouptype = kwargs['grouptype']

        if 'regdate' in kwargs:
            self.regdate = datetime.datetime.today()

        if 'cancel_yn' in kwargs:
            self.cancel_yn = kwargs['cancel_yn']

        if 'canceldate' in kwargs:
            self.canceldate = kwargs['canceldate']

        if 'cancel_reason' in kwargs:
            self.cancel_reason = kwargs['cancel_reason']

        if 'memo' in kwargs:
            self.memo = kwargs['memo']

    def get_id(self):
        return self.idx

    @classmethod
    def get(cls, idx):
        try:
            return db.db_session.query(cls).filter(cls.idx == idx).one()
        except NoResultFound:
            return None

    @classmethod
    def find(cls, camp_idx, groupid):
        try:
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.groupid == groupid).one()
        except NoResultFound:
            return None

    @classmethod
    def get_list(cls, camp_idx):
        try:
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx).all()
        except NoResultFound:
            return None

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
        try:
            return db.db_session.query(cls).filter(cls.idx == idx).one()
        except NoResultFound:
            return None

    @classmethod
    def get(cls, camp_idx, church_name):
        try:
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.church_name == church_name).one()
        except NoResultFound:
            return None

    @classmethod
    def get_list(cls, camp_idx):
        try:
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx).all()
        except NoResultFound as e:
            return None

    @classmethod
    def insert(cls, camp_idx, church_name, name, address, contact, memo):
        promotion = cls(camp_idx, church_name, name, address, contact, memo)
        db.db_session.add(promotion)
        db.db_session.commit()
