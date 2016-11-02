# -*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
import os
import sys

from flask import Flask, render_template
from cross import views_main
from cross.views import CmcView, CbtjView, WsView, YouthView, KidsView
from cross.views_master import master
# from parking import context as parking


cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.insert(0, root_dir)
context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

# import logging
# from logging import FileHandler

# logger = logging.getLogger('werkzeug')
# logger.setLevel(logging.DEBUG)
# logging.basicConfig(stream=sys.stderr)
# file_handler = FileHandler('/home/intercp/logs/missioncamp/error.log')
# file_handler.setLevel(logging.DEBUG)

# access log
# logger.addHandler(file_handler)

# error log for 500
# context.logger.addHandler(file_handler)


cmc_view = CmcView()
context.register_blueprint(cmc_view.context)
cbtj_view = CbtjView()
context.register_blueprint(cbtj_view.context)
ws_view = WsView()
context.register_blueprint(ws_view.context)
youth_view = YouthView()
context.register_blueprint(youth_view.context)
kids_view = KidsView()
context.register_blueprint(kids_view.context)
context.register_blueprint(master)
# context.register_blueprint(parking)

views_main.register_view(context)

'''
# 500에러 발생시 로그에 기록
@context.errorhandler(500)
def internal_error(exception):
    context.logger.error(exception)
    print >> sys.stderr, exception
    return "500 Internal Server Error", 500
'''
