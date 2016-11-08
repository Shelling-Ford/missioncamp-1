'''missioncamp.app.py
'''
import os
import sys

from flask import Flask, render_template, request
from flask_babel import Babel

from core.database import DB as db
from missioncamp.views import get_app

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

APP.register_blueprint(get_app('cbtj'))
APP.register_blueprint(get_app('cmc'))
APP.register_blueprint(get_app('kids'))
APP.register_blueprint(get_app('ws'))
APP.register_blueprint(get_app('youth'))

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
