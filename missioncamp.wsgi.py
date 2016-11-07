#!/usr/bin/python
# pylint: disable=W0611,W0122,C0413
'''
아파치에서 mod_wsgi를 통해 load되는 모듈
missioncamp
'''
import os
import sys
import logging

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)
logging.basicConfig(stream=sys.stderr)

ACTIVATE_THIS = os.path.join(CUR_DIR, 'env/bin/activate_this.py')
with open(ACTIVATE_THIS) as f:
    CODE = compile(f.read(), ACTIVATE_THIS, 'exec')
    exec(CODE)

from missioncamp.app import APP as application
