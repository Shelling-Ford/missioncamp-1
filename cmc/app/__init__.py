#-*-coding:utf-8-*-
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
