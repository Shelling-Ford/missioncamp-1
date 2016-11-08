'''
캠프코드를 이용해 전체 통계를 구해주는 모듈
'''
# pylint: disable=C0103
from sqlalchemy import func
from sqlalchemy.sql import text
from core.database import DB as db
from core.models import Member, Membership, Camp
from cross.stat_metrics import METRICS as metrics


def get_query(camp_idx, *args, group_by=None):
    '''
    항목별 통계를 쉽게 뽑아내기 위한 메타쿼리
    '''
    if group_by is None:
        base_query = db.session.query(func.count('*'), func.count(Member.payment), func.sum(Member.attend_yn))
    else:
        base_query = db.session.query(getattr(Member, group_by), func.count('*'), func.count(Member.payment), func.sum(Member.attend_yn))
    base_query = base_query.select_from(Member).outerjoin(Member.payment).filter(Member.camp_idx == camp_idx, Member.cancel_yn == 0)

    filtered_query = base_query
    for key, value in args:
        if value in ['none', 'not_none']:
            if value == 'none':
                filtered_query = filtered_query.filter(getattr(Member, key).is_(None))
            else:
                filtered_query = filtered_query.filter(getattr(Member, key).isnot(None))
        else:
            filtered_query = filtered_query.filter(getattr(Member, key) == value)

    if group_by is not None:
        filtered_query = filtered_query.group_by(getattr(Member, group_by))

    return filtered_query


def get_membership_query(camp_idx, membership_key):
    '''
    가변필드를 기준으로 한 메타쿼리
    '''
    base_query = db.session.query(Membership.value, func.count('*'), func.count(Member.payment), func.sum(Member.attend_yn))
    base_query = base_query.select_from(Member).outerjoin(Member.payment).outerjoin(Member.membership).filter(Member.camp_idx == camp_idx, Member.cancel_yn == 0)

    filtered_query = base_query.filter(Membership.key == membership_key).group_by(Membership.value)
    return filtered_query


def get_stat(camp_idx):
    '''
    통계
    '''
    results = dict()
    basic = dict()
    for key, value in metrics['basic'].items():
        basic[key] = get_query(camp_idx, *value).one()
    results['basic'] = basic

    group_by = dict()
    for key, value in metrics['group_by'].items():
        rows = get_query(camp_idx, group_by=value).all()
        group_by[key] = (value, rows)
    results['group_by'] = group_by

    camp = db.session.query(Camp).filter(Camp.idx == camp_idx).one()
    membership = dict()
    for key, value in metrics["membership"][camp.code].items():
        rows = get_membership_query(camp_idx, value).all()
        membership[key] = (value, rows)
    results['membership'] = membership

    # 연령별 통계
    query = text("""
        SELECT CONCAT(`ages`,'대') `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM (
            SELECT LEFT(%s-(MID(`m`.`birth`,1,4)),1)*10 AS `ages`, `p`.`amount` `amount`, `m`.`attend_yn` `attend_yn`
            FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
            WHERE (`camp_idx` = %s) AND `cancel_yn` = 0
        ) `mem`
        GROUP BY `mem`.`ages`
    """ % (camp.year, camp_idx))
    results['ages'] = db.session.execute(query)
    return results
