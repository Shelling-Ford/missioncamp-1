#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import logging
from runcross import app, cur_dir

sys.path.append(cur_dir)
logging.basicConfig(stream=sys.stderr)

activate_this = os.path.join(cur_dir, 'env/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

application = app

