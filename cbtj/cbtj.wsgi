#!/usr/bin/python
# import sys
# sys.path.insert(0,"/home/missioncamp/public_html/missioncamp/")

import logging
logging.basicConfig(stream=sys.stderr)


activate_this = '/home/missioncamp/.venv/missioncamp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import app as application

# add views
# import app.views

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=False)
