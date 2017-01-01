''' 크로스 메인 모듈
'''
import os
import sys

from flask import Flask
from core.database import DB as db
from core.models import Area, Group, Membership
from cross import views_main
from cross.views import get_app
from cross.views_master import MASTER as master

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CUR_DIR))
sys.path.insert(0, ROOT_DIR)
APP = Flask(__name__)
APP.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

# register views and blueprints to APP
views_main.register_view(APP)
APP.register_blueprint(get_app('cbtj'))
APP.register_blueprint(get_app('cmc'))
APP.register_blueprint(get_app('kids'))
APP.register_blueprint(get_app('ws'))
APP.register_blueprint(get_app('youth'))
APP.register_blueprint(master)


# template filters
@APP.template_filter("area_name")
def area_name(idx):
    '''
    area_idx로 지부 이름을 반환함.
    '''
    area = db.session.query(Area).filter(Area.idx == idx).one()
    return area.name


@APP.template_filter("group_name")
def group_name(idx):
    '''
    group_idx로 단체 이름을 반환함.
    '''
    if idx is not None:
        group = db.session.query(Group).filter(Group.idx == idx).one()
        return group.name
    else:
        return '없음'


@APP.template_filter("intercp_training")
def intercp_training(idx):
    memberships = db.session.query(Membership).filter(Membership.member_idx == idx, Membership.key == 'training').all()
    return ",".join([m.value for m in memberships])


@APP.template_filter("membership")
def membership(idx, membership_key):
    result = db.session.query(Membership).filter(Membership.member_idx == idx, Membership.key == membership_key).first()
    if result is not None:
        return result.value
    else:
        return ""
