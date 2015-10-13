from app import context
from flask import render_template, redirect, url_for

@context.route('/')
def home():
    return render_template('home.html')

@context.route('/invitation')
def invitation():
    return render_template('invitation.html')

@context.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')

@context.route('/camp')
def camp():
    return redirect(url_for('home'))
