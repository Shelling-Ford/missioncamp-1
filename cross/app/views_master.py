#-*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint
#from flask.helpers import make_response
from flask_login import login_required,current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

from core.models import Area, Room, GlobalOptions
from core.forms.master import AreaForm

#import functions_mongo as mongo
#import xlsxwriter

# Blueprint 초기화
master = Blueprint('master', __name__, template_folder='templates', url_prefix='/master')

master_permission = Permission(RoleNeed('master'))

@master.route('/')
@login_required
@master_permission.require(http_exception=403)
def home():
	current_year = GlobalOptions.get_year()
	current_term = GlobalOptions.get_term()
	return render_template('master/home.html', current_year=current_year, current_term=current_term)

@master.route('/area-list')
@login_required
@master_permission.require(http_exception=403)
def area_list():
    area_list = Area.get_list('*')
    return render_template('master/area_list.html', area_list=area_list)

@master.route('/area', methods=['GET', 'POST'])
@login_required
@master_permission.require(http_exception=403)
def area():
	if request.method == 'POST':
		idx = request.form.get('idx', None)
		name = request.form.get('name')
		type = request.form.get('type')
		camp = request.form.get('camp')

		if idx is None:
			Area.insert(name, type, camp)
		else:
			Area.update(idx, name, type, camp)

		return redirect(url_for('.area_list'))

	else:
		area_idx = request.args.get('area_idx', None)
		
		form = AreaForm()

		if area_idx is not None:
			area = Area.get(area_idx)
			form.set_area_data(area)

		return render_template('master/form.html', form=form)

@master.route('/room-list')
@login_required
@master_permission.require(http_exception=403)
def room_list():
	room_list = Room.get_list()
	return render_template('master/room_list.html', room_list=room_list)