# -*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
from flask import Flask, render_template, request
from flask_babel import Babel

from views.cbtj import context as cbtj
from views.cmc import context as cmc
from views.kids import context as kids
from views.ws import context as ws
from views.youth import context as youth

from core.database import db

import os
import sys


cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

babel = Babel(context)


@babel.localeselector
def get_locale():
    lang = request.args.get('lang')
    if lang is None:
        lang = request.accept_languages.best_match(['ko', 'ko_KR', 'en', 'en_US', 'en_GB'])
    return lang


context.register_blueprint(cbtj)
context.register_blueprint(cmc)
context.register_blueprint(kids)
context.register_blueprint(ws)
context.register_blueprint(youth)

db.Base.metadata.create_all(db.engine)


@context.route('/')
def index():
    return render_template('index.html')
