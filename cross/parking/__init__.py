# -*-coding:utf-8-*-
from flask import render_template, flash, redirect, url_for, session, request, Blueprint, abort
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed
from jinja2 import TemplateNotFound

# Blueprint 초기화
context = Blueprint('parking', __name__, template_folder='templates', url_prefix='/parking')


@context.route('/')
def home():
    return render_template('parking/home.html')
