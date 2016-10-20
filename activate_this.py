# -*- coding: utf-8 -*-
import os
import sys
import logging

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
logging.basicConfig(stream=sys.stderr)

activate_this = os.path.join(cur_dir, 'env/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))