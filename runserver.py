from missioncamp.app import app
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
