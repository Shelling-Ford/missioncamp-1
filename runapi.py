# -*- coding: utf-8 -*-
from api.app import APP as app
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555, debug=True)
