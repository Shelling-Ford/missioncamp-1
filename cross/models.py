'''
크로스에서 인증 및 로그인에 사용하는 데이터베이스 관계형 매핑 모듈
'''
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from core.database import BTJKOREA_DB as btjkorea_db
from core.database import DB as db

class AdminUser(db.base, UserMixin):
    '''
    크로스 사용자
    '''
    __tablename__ = 'admin'

    idx = Column(Integer, primary_key=True)
    adminid = Column(String)
    adminpw = Column(String)
    role = Column(String)
    camp = Column(String)
    chaptercode = Column(String)
    area_idx = Column(Integer)

    def get_id(self):
        return self.adminid


# BTJKorea 인증을 위한 모델 클래스
class BtjUser(btjkorea_db.base):
    '''
    BTJKorea 인증을 위한 사용자
    '''
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
