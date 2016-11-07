#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import logging

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
logging.basicConfig(stream=sys.stderr)

activate_this = os.path.join(cur_dir, 'env/bin/activate_this.py')
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code)

from cross.app import APP as application
