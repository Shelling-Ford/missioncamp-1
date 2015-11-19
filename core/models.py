#-*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound
from core.database import db

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
            return db.db_session.query(cls).filter(cls.camp_idx == camp_idx and cls.church_name == church_name).one()
        except NoResultFound:
            return None

    @classmethod
    def insert(cls, camp_idx, church_name, name, address, contact, memo):
        promotion = cls(camp_idx, church_name, name, address, contact, memo)
        db.db_session.add(promotion)
        db.db_session.commit()
