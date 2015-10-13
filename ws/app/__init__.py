#-*-coding:utf-8-*-
from flask import Flask

context = Flask(__name__)
context.secret_key = 'r&rbtrtk3hd36u#9k=8cb*!m@8o1t)zp=mws#s&a!jvvty9yis'
# context.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:btj1040!@localhost/mcampadm'

import views
