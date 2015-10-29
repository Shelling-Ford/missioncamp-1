#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, Blueprint

context = Blueprint('ws', __name__, template_folder='templates', url_prefix='/ws')

@context.route('/')
def home():
    return render_template('ws/home.html')

@context.route('/invitation')
def invitation():
    return render_template('ws/invitation.html')

@context.route('/recommendation')
def recommendation():
    return render_template('ws/recommendation.html')

@context.route('/camp')
def camp():
    return redirect(url_for('home'))
