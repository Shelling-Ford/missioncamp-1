#-*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__)) #현재 디렉터리 위치를 프로그램적으로 반환해줌 missioncamp/site/app`
root_dir = os.path.dirname(os.path.dirname(cur_dir)) #부모의 부모 디렉터리를 반환해줌 missioncamp
sys.path.insert(0,root_dir) #missioncamp를 path환경변수에 추가하여 core 패키지에 접근할 수 있도록 함.
sys.path.insert(0,cur_dir) #missioncamp/site/app을 path환경변수에 추가하여 functions나 views 패키지에 접근할 수 있도록 함.

from flask import Flask, render_template, request

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

from flask_babel import Babel
babel = Babel(context)

@babel.localeselector
def get_locale():
    lang = request.args.get('lang')
    if lang == None:
        lang = request.accept_languages.best_match(['ko', 'ko_KR', 'en', 'en_US', 'en_GB'])
    return lang

from views.cbtj import context as cbtj
context.register_blueprint(cbtj)
from views.cmc import context as cmc
context.register_blueprint(cmc)
from views.kids import context as kids
context.register_blueprint(kids)
from views.ws import context as ws
context.register_blueprint(ws)
from views.youth import context as youth
context.register_blueprint(youth)

@context.route('/')
def index():
    return render_template('index.html')
