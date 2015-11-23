#-*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, Date, ForeignKey, desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from core.database import db
import datetime

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
        return db.db_session.query(cls).filter(cls.idx == idx).first()

    @classmethod
    def find(cls, camp_idx, userid):
        return db.db_session.query(cls).filter(cls.camp_idx == camp_idx, cls.userid == userid).first()

    @classmethod
    def get_list(cls, camp_idx, **kwargs):
        result = db.db_session.query(cls).join(Member.area).outerjoin(Member.group).outerjoin(Member.payment).filter(cls.camp_idx == camp_idx)
        for key, value in kwargs.iteritems():
            if value is not None and value != '':
                attr = getattr(cls, key)
                result = result.filter(attr == value)

        return result.order_by(desc(cls.idx)).all()

    @classmethod
    def get_old_list(cls, camp_idx, offset=None, **kwargs):
        result = db.db_session.query(cls).join(Member.area).outerjoin(Member.membership).filter(cls.camp_idx == camp_idx)
        for key, value in kwargs.iteritems():
            if value is not None and value != '':
                attr = getattr(cls, key)
                result = result.filter(attr == value)

        result = result.order_by(desc(cls.idx))

        if offset is not None:
            return result.limit(200).offset(offset).all()
        else:
            return result.all()

    @classmethod
    def count(cls, camp_idx, **kwargs):
        result = db.db_session.query(cls).join(Area).outerjoin(Group).outerjoin(Payment).filter(cls.camp_idx == camp_idx)
        for key, value in kwargs.iteritems():
            if value is not None and value != '':
                attr = getattr(cls, key)
                result = result.filter(attr == value)

        return result.count()

    @classmethod
    def update(cls, member_idx, **kwargs):
        member = cls.get(member_idx)
        if member is not None:
            for key, value in kwargs.iteritems():
                if value is not None and value != '':
                    setattr(member, key, value)

        db.db_session.commit()
