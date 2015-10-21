#-*-coding:utf-8-*-
# 공유 패키지에서 함수를 호출하기 위해 path지정을 해줌
import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cur_dir))
sys.path.insert(0,root_dir)
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'

import views
from views_cmc import cmc
from views_cbtj import cbtj
context.register_blueprint(cmc)
context.register_blueprint(cbtj)
