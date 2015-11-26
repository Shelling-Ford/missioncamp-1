#-*-coding:utf-8-*-
from core.models import Camp
def get_camp_idx(camp, year=None, term=None):
    return Camp.get_idx(camp, year, term)
