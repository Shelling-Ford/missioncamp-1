# -*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.insert(0, root_dir)
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

import views_main

from views import CmcView
cmc_view = CmcView()
context.register_blueprint(cmc_view.context)

from views import CbtjView
cbtj_view = CbtjView()
context.register_blueprint(cbtj_view.context)

from views import WsView
ws_view = WsView()
context.register_blueprint(ws_view.context)

from views import YouthView
youth_view = YouthView()
context.register_blueprint(youth_view.context)

from views import KidsView
kids_view = KidsView()
context.register_blueprint(kids_view.context)


from views_master import master
context.register_blueprint(master)

from parking import context as parking
context.register_blueprint(parking)
