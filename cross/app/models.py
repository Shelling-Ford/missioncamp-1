# -*-coding:utf-8-*-
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Date, or_
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.exc import NoResultFound
from core.database import btjkorea_db
from core.database import db


class AdminUser(db.Base, UserMixin):
    __tablename__ = 'admin'

    idx = Column(Integer, primary_key=True)
    adminid = Column(String)
    adminpw = Column(String)
    role = Column(String)
    camp = Column(String)
    chaptercode = Column(String)
    area_idx = Column(Integer)

    def __init__(self, idx, adminid, adminpw, role, camp, area_idx):
        self.idx = idx
        self.adminid = adminid
        self.adminpw = adminpw
        self.role = role
        self.camp = camp
        self.area_idx = area_idx

    @classmethod
    def login_check(cls, adminid, pwd):
        results = db.execute("SELECT * FROM `admin` WHERE adminid = '%s' AND adminpw = '%s'" % (adminid, pwd))
        if len(results) > 0:
            return True
        else:
            return False

    def get_id(self):
        return self.adminid

    @classmethod
    def get(cls, id):
        try:
            return db.db_session.query(cls).filter(cls.adminid == id).one()
        except NoResultFound:
            return None


import datetime


class ModelSerializer():

    def _todict(self, found=None):
        if found is None:
            found = set()

        mapper = class_mapper(self.__class__)
        columns = [column.key for column in mapper.columns]
        get_key_value = lambda c: (c, getattr(self, c).strftime('%Y-%m-%d %H:%M:%S')) if isinstance(getattr(self, c), datetime.datetime) else (c, getattr(self, c))
        out = dict(map(get_key_value, columns))
        for name, relation in mapper.relationships.items():
            if relation not in found:
                found.add(relation)
                related_obj = getattr(self, name)
                if related_obj is not None:
                    if relation.uselist:
                        out[name] = [child._todict(found) for child in related_obj]
                    else:
                        out[name] = related_obj._todict(found)
        return out


# BTJKorea 인증을 위한 모델 클래스
class BtjUser(btjkorea_db.Base, ModelSerializer, UserMixin):
    __tablename__ = 'g5_member'

    mb_no = Column(Integer, primary_key=True)
    mb_id = Column(String)
    mb_password = Column(String)
    mb_name = Column(String)
    mb_level = Column(Integer)
    mb_sex = Column(String)
    mb_hp = Column(String)
    chaptercode = Column(String)
    role = ""
    camp = ""

    @classmethod
    def login_check(cls, mb_id, pwd):
        results = btjkorea_db.execute("SELECT * FROM `g5_member` WHERE mb_id = '%s' AND mb_password = PASSWORD('%s')" % (mb_id, pwd))
        if len(results) > 0:
            return True
        else:
            return False

    def get_id(self):
        return self.mb_id

    @classmethod
    def get(cls, **kwargs):
        result = btjkorea_db.session.query(cls)

        if 'mb_id' in kwargs:
            btjuser = result.filter(cls.mb_id == kwargs['mb_id']).one()
            if btjuser.chaptercode == '01':
                btjuser.role = 'hq'
            else:
                btjuser.role = 'branch'

            btjuser.camp = "cmc,cbtj,ws,youth,kids"
            return btjuser

        for key, value in kwargs.iteritems():
            filter_list = None
            if value is not None and value != '':
                value = [value] if type(value) is not list else value

                filter_list = []
                for v in value:
                    filter_list.append(getattr(cls, key) == v)

                if filter_list is not None:
                    result = result.filter(or_(*filter_list))

            return result.all()
