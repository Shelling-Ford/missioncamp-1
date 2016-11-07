''' 개발환경에서 서버를 실행하기 위한 모듈
'''
from missioncamp.app import APP as app
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
