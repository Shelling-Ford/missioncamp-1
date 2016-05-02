#!/usr/bin/python
import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_dir)

import logging
logging.basicConfig(stream=sys.stderr)

activate_this = '/home/intercp/PYENV/missioncamp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from werkzeug.debug import DebuggedApplication
from app import context as app
application = DebuggedApplication(app, True)

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
