''' 크로스 메인 모듈
'''
import os
import sys

from flask import Flask
from cross import views_main
from cross.views import get_app
from cross.views_master import master

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
