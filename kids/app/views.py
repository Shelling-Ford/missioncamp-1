#-*-coding:utf-8-*-
from app import context
from flask import render_template, redirect, url_for

@context.route('/')
def home():
    return render_template('home.html')
