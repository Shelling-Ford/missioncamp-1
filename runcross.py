# -*- coding: utf-8 -*-
from cross.app import context as app
# from cross import context as cross
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
