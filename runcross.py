# -*- coding: utf-8 -*-
from cross.app import APP as app
# from cross import context as cross
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
