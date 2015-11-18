from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound
from core.database import db

class AdminUser(db.Base, UserMixin):
    __tablename__ = 'admin'

    idx = Column(Integer, primary_key=True)
    adminid = Column(String)
    adminpw = Column(String)
    role = Column(String)
    camp = Column(String)

    def __init__(self, idx, adminid, adminpw, role, camp):
        self.idx = idx
        self.adminid = adminid
        self.adminpw = adminpw
        self.role = role
        self.camp = camp

    def get_id(self):
        return self.adminid

    @classmethod
    def get(cls, id):
        try:
            return db.db_session.query(cls).filter(cls.adminid == id).one()
        except NoResultFound:
            return None
