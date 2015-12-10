#-*-coding:utf-8-*-
activate_this = '/Users/intercp/.venv/missioncamp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from app import context

if __name__ == '__main__':
    context.run(host='0.0.0.0', debug=True)
