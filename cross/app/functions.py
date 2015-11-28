#-*-coding:utf-8-*-
from sqlalchemy.sql import text
from core.database import db
from core.functions import getMembership
import datetime

def login_check(camp, id, pwd):
    results = db.execute("SELECT * FROM `admin` WHERE `adminid` = :id AND `adminpw` = :pwd AND `camp` = :camp", {'id': id, 'pwd': pwd, 'camp': camp})
    if len(results) == 1:
        return results[0]['role']
    else:
        return 0

# 기본 통계
def get_basic_stat(camp_idx, camp_idx2=None):
    query_option = ' OR `m`.`camp_idx` = %s ' % camp_idx2 if camp_idx2 is not None else ''
    sql = []
    # 전체
    sql.append(text("""
        SELECT 'total' as 'tag', '전체' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0
    """ % query_option))
    # 개인
    sql.append(text("""
        SELECT '개인' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NULL
    """ % query_option))
    # 단체
    sql.append(text("""
        SELECT '단체' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NOT NULL
    """ % query_option))
    # 성별
    sql.append(text("""
        SELECT CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 GROUP BY `sex`
    """ % query_option))
    # 개인 성별
    sql.append(text("""
        SELECT CONCAT('개인 ', CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END) as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NULL GROUP BY `sex`
    """ % query_option))
    # 단체 성별
    sql.append(text("""
        SELECT CONCAT('단체 ', CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END) as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NOT NULL GROUP BY `sex`
    """ % query_option))

    query_params = {'camp_idx': camp_idx}

    stat = {
        'summary':[], 'area':[], 'persontype':[], 'group_name':[], 'campus': [],
        'training':[], 'job': [],
    }
    for s in sql:
        results = db.execute(s, query_params)
        for r in results:
            stat['summary'].append(dict(r))

    query = text("""
        SELECT `a`.`idx` `idx`, `a`.`idx` `param`, `a`.`name` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `area` `a` ON `m`.`area_idx` = `a`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `cancel_yn` = 0 GROUP BY `a`.`name`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['area'].append(dict(r))

    query = text("""
        SELECT `m`.`persontype` `name`, `m`.`persontype` `param`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `cancel_yn` = 0 GROUP BY `persontype`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['persontype'].append(dict(r))

    query = text("""
        SELECT `g`.`idx` `idx`, `g`.`idx` `param`, `g`.`name` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 GROUP BY `g`.`name`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['group_name'].append(dict(r))

    query = text("""
        SELECT `ms`.`value` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'campus' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['campus'].append(dict(r))

    query = text("""
        SELECT `ms`.`value` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'training' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['training'].append(dict(r))

    query = text("""
        SELECT `ms`.`value` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE `m`.`camp_idx` = :camp_idx %s AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'job' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.execute(query, query_params)
    for r in results:
        stat['job'].append(dict(r))

    return stat

from core.models import Member
# member 목록 열람
def get_member_list(camp_idx, **kwargs):
    return Member.get_list(camp_idx, kwargs)

# member 정보 열람
def get_member(member_idx):
    param = {"member_idx": member_idx}
    query = text("SELECT * FROM `member` WHERE `idx` = :member_idx")
    member = db.select_one(query, param)
    return member

# membership 정보 열람
def get_membership(member_idx):
    param = {"member_idx": member_idx}
    query = text("SELECT * FROM `membership` WHERE `member_idx` = :member_idx")
    membership = getMembership(db.select_all(query, param))
    return membership

# 재정정보 열람
def get_payment(member_idx):
    param = {"member_idx": member_idx}
    query = text("SELECT * FROM `payment` WHERE `member_idx` = :member_idx")
    payment = db.select_one(query, param)
    return payment

# 재정정보 입력
def save_payment(**kwargs):
    if kwargs['paydate'] == None or kwargs['paydate'] == u'':
        kwargs['paydate'] = "%s" % datetime.datetime.today().date()

    payment = get_payment(kwargs['member_idx'])

    if payment is None:
        query = text("""
            INSERT INTO
                `payment`(`member_idx`, `amount`, `complete`, `claim`, `paydate`, `staff_name`)
            VALUES
                (:member_idx, :amount, :complete, :claim, :paydate, :staff_name)
        """)
    else:
        query = text("""
            UPDATE `payment` SET
                `amount` = :amount,
                `complete` = :complete,
                `claim` = :claim,
                `paydate` = :paydate,
                `staff_name` = :staff_name
            WHERE
                `member_idx` = :member_idx
        """)

    db.raw_query(query, kwargs)
    db.commit()

# 재정정보 삭제
def delete_payment(member_idx):
    db.raw_query("DELETE FROM `payment` WHERE `member_idx`= :member_idx", {'member_idx': member_idx})
    db.commit()

# 숙소 목록을 불러옴
def get_room_list():
    results = db.select_all("SELECT * FROM `room` ORDER BY `building`, `number`")
    return results

# 신청자에 숙소배치 정보를 등록해줌
def set_member_room(**kwargs):
    db.raw_query("UPDATE `member` SET `room_idx` = :room_idx WHERE `idx` = :member_idx", kwargs)
    db.commit()
