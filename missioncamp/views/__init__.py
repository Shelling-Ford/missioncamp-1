from flask import Blueprint
from flask import render_template, request, flash, session, redirect, url_for
from jinja2 import TemplateNotFound

from core.forms import RegistrationForm
from core.models import Member, Area


def get_app(campcode):
    if campcode in ['cmc', 'cbtj', 'ws', 'kids', 'youth']:
        app = Blueprint(campcode, __name__, template_folder='templates', url_prefix='/{0}'.format(campcode))
        register_view(app, campcode)
        return app
    else:
        return None


def register_view(app, campcode):
    # home - Main page for each Camp
    @app.route('/')
    def home():
        return render_template("{0}/home.html".format(campcode))

    # page - Static page for camp information
    @app.route('/<page_id>')
    def page(page_id):
        try:
            return render_template('{0}/{1}.html'.format(campcode, page_id))
        except TemplateNotFound:
            return render_template('{0}/404.html'.format(campcode))

    @app.route("/registration", methods=['GET', 'POST'])
    def registration():
        form = RegistrationForm(request.form)
        form.set_camp(campcode)

        if request.method == "POST":
            idx = form.insert()
            flash('신청이 완료되었습니다.')
            session['type'] = u'개인'
            session['idx'] = idx
            return redirect(url_for('.member_info'))
        params = {
            'form': form,
            'page_header': "개인신청",
            'script': url_for('static', filename='cmc/js/reg-individual.js')
        }
        return render_template('{0}/form.html'.format(campcode), **params)

    @app.route("/member-info")
    def member_info():
        idx = session['idx']
        member = Member.get(idx)
        params = {
            'camp': campcode,
            'member': member,
            'membership_data': member.get_membership_data(),
            'area_name': Area.get_name(member.area_idx)
        }
        return render_template('cmc/individual/show.html', **params)
