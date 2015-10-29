#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, Blueprint

context = Blueprint('kids', __name__, template_folder='templates', url_prefix='/kids')

@context.route('/')
def home():
    return render_template('kids/home.html')
