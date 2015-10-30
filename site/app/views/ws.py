#-*-coding:utf-8-*-
from flask import render_template, redirect, url_for, Blueprint
from core.functions import *

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

# 아이디 중복체크
@context.route('/individual/check-userid', methods=['POST'])
@context.route('/group/member/check-userid', methods=['POST'])
def check_userid():
    campidx = getCampIdx('ws')
    userid = request.form.get('userid')
    return "%d" % checkUserId(campidx, userid)

# 개인신청 - 신청서
@context.route('/individual/add')
def reg_individual():
    campidx = getCampIdx('ws')
    area_list = getAreaList('ws') # form에 들어갈 지부 목록
    date_select_list = getDateSelectList() # form 생년월일에 들어갈 날자 목록
    return render_template('ws/individual/add.html', camp='ws', campidx=campidx,
        area_list=area_list, date_select_list=date_select_list, group_yn=False)
