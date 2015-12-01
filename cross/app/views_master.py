#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
from flask.helpers import make_response
from flask_login import login_required,current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.functions import *
from core.models import Area

from functions import *
import functions_mongo as mongo
import xlsxwriter

# Blueprint 초기화
master = Blueprint('master', __name__, template_folder='templates', url_prefix='/master')

master_permission = Permission(RoleNeed('master'))

@master.route('/')
@login_required
@master_permission.require(http_exception=403)
def home():
    return render_template('master/home.html')

@master.route('/area-list')
@login_required
@master_permission.require(http_exception=403)
def area_list():
    area_list = Area.get_list('*')
    return render_template('master/area_list.html', area_list=area_list)
