'''
크로스 최종관리자 설정을 위한 화면
'''
from flask import render_template, redirect, url_for, request, Blueprint
from flask_login import login_required
from sqlalchemy.orm.exc import NoResultFound
from core.models import Area, Room, GlobalOptions
from core.database import DB as db
from core.forms import AreaForm


# Blueprint 초기화
MASTER = Blueprint('master', __name__, template_folder='templates', url_prefix='/master')


@MASTER.route('/')
@login_required
def home():
    '''
    현재 년도와 현제 텀을 보여줌.
    '''
    year = int(db.session.query(GlobalOptions).filter(GlobalOptions.key == 'current_year').one().value)
    term = int(db.session.query(GlobalOptions).filter(GlobalOptions.key == 'current_term').one().value)

    return render_template('master/home.html', current_year=year, current_term=term)


@MASTER.route('/area-list')
@login_required
def area_list():
    '''
    전체 지부 목록
    '''
    a_list = db.session.query(Area).order_by(Area.type).all()
    return render_template('master/area_list.html', area_list=a_list)


@MASTER.route('/area', methods=['GET', 'POST'], defaults={"idx": None})
@MASTER.route('/area/<idx>', methods=['GET', 'POST'])
@login_required
def area(idx):
    '''
    지부 수정
    '''
    if request.method == 'POST':
        name = request.form.get('name')
        area_type = request.form.get('type')
        camp = request.form.get('camp')

        if idx is None:
            '''
            지부 추가를 할 경우인데 이름이 겹치는지 확인할 것
            '''
            try:
                area_obj = db.session.query(Area).filter(Area.name == name, Area.type == area_type).one()
            except NoResultFound:
                area_obj = Area()
        else:
            area_obj = db.session.query(Area).filter(Area.idx == idx).one()

        area_obj.name = name
        area_obj.type = area_type
        area_obj.camp = camp

        if area_obj.idx is None:
            db.session.add(area_obj)
        db.session.commit()

        return redirect(url_for('.area_list'))

    area_idx = request.args.get('area_idx', None)
    form = AreaForm()

    if area_idx is not None:
        area_obj = db.session.query(Area).filter(Area.idx == area_idx).one()
        form.set_area_data(area_obj)

    return render_template('master/form.html', form=form)


@MASTER.route('/room-list')
@login_required
def room_list():
    '''
    숙소 전체목록 보기
    '''
    r_list = db.session.query(Room).order_by(Room.building, Room.number).all()
    return render_template('master/room_list.html', room_list=r_list)
