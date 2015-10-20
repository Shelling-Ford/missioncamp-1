#-*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.insert(0,root_dir)

from flask import Flask, request

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'
# context.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:btj1040!@localhost/mcampadm'

from flask_babel import Babel

babel = Babel(context)

@babel.localeselector
def get_locale():
    lang = request.args.get('lang')
    if lang == None:
        lang = request.accept_languages.best_match(['ko', 'ko_KR', 'en', 'en_US', 'en_GB'])
    return lang

import views
