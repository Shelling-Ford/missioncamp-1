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

from core.database import db
from missioncamp.views import get_app

import os
import sys


cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

app = Flask(__name__)
app.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

babel = Babel(app)


@babel.localeselector
def get_locale():
    lang = request.args.get('lang')
    if lang is None:
        lang = request.accept_languages.best_match(['ko', 'ko_KR', 'en', 'en_US', 'en_GB'])
    return lang

cbtj_app = get_app('cbtj')
cmc_app = get_app('cmc')
kids_app = get_app('kids')
ws_app = get_app('ws')
youth_app = get_app('youth')
app.register_blueprint(cbtj_app)
app.register_blueprint(cmc_app)
app.register_blueprint(kids_app)
app.register_blueprint(ws_app)
app.register_blueprint(youth_app)

db.Base.metadata.create_all(db.engine)


@app.route('/')
def index():
    return render_template('index.html')

# template filters
@app.template_filter("yesno")
def yesno(value):
    return '예' if value else '아니오'

@app.template_filter("sex")
def sex(value):
    if value == 'M':
        return '남자'
    elif value == 'F':
        return '여자'
    else:
        return '오류'
