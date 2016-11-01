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
app.register_blueprint(cbtj_app)
app.register_blueprint(cmc_app)
# context.register_blueprint(kids)
# context.register_blueprint(ws)
# context.register_blueprint(youth)

db.Base.metadata.create_all(db.engine)


@app.route('/')
def index():
    return render_template('index.html')
