#!/usr/bin/python
import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_dir)

import logging
logging.basicConfig(stream=sys.stderr)


activate_this = '/Users/intercp/.venv/missioncamp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from app import context as application

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
