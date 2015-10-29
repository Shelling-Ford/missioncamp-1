#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, Blueprint

context = Blueprint('youth', __name__, template_folder='templates', url_prefix='/youth')

@context.route('/')
def home():
    return render_template('youth/home.html')
