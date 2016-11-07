'''missioncamp.app.py
'''
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
from flask import Flask, render_template, request
from flask_babel import Babel

# from missioncamp.views.cbtj import context as cbtj
# from missioncamp.views.cmc import context as cmc
# from missioncamp.views.kids import context as kids
# from missioncamp.views.ws import context as ws
# from missioncamp.views.youth import context as youth

from core.database import DB as db
from missioncamp.views import get_app

import os
import sys


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)

APP = Flask(__name__)
APP.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

BABEL = Babel(APP)


@BABEL.localeselector
def get_locale():
    '''
    언어 선택기
    '''
    lang = request.args.get('lang')
    if lang is None:
        lang = request.accept_languages.best_match(['ko', 'ko_KR', 'en', 'en_US', 'en_GB'])
    return lang

CBTJ_APP = get_app('cbtj')
CMC_APP = get_app('cmc')
KIDS_APP = get_app('kids')
WS_APP = get_app('ws')
YOUTH_APP = get_app('youth')
APP.register_blueprint(CBTJ_APP)
APP.register_blueprint(CMC_APP)
APP.register_blueprint(KIDS_APP)
APP.register_blueprint(WS_APP)
APP.register_blueprint(YOUTH_APP)

db.base.metadata.create_all(db.engine)


@APP.route('/')
def index():
    '''
    선교캠프 통합 메인 페이지
    '''
    return render_template('index.html')

# template filters
@APP.template_filter("yesno")
def yesno(value):
    '''
    value가 false이거나 None이면 아니오, 나머지는 예를 출력하도록 하는 템플릿 필터
    '''
    return '예' if value else '아니오'

@APP.template_filter("sex")
def sex(value):
    '''
    성별을 한글로 출력해주는 템플릿 필터
    '''
    if value == 'M':
        return '남자'
    elif value == 'F':
        return '여자'
    else:
        return '오류'
