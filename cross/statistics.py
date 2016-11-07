'''
캠프코드를 이용해 전체 통계를 구해주는 모듈
'''
from sqlalchemy.sql import text
from core.database import DB as db

def get_basic_stat(camp_idx):
    '''
    캠프코드를 이용해 전체 통계를 구해주는 함수
    '''
    query_option = ''
    sql = []
    # 전체
    sql.append(text("""
        SELECT 'total' as 'tag', '전체' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0
    """ % query_option))
    # 개인
    sql.append(text("""
        SELECT '개인' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NULL
    """ % query_option))
    # 단체
    sql.append(text("""
        SELECT '단체' as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NOT NULL
    """ % query_option))
    # 성별
    sql.append(text("""
        SELECT CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 GROUP BY `sex`
    """ % query_option))
    # 개인 성별
    sql.append(text("""
        SELECT CONCAT('개인 ', CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END) as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NULL GROUP BY `sex`
    """ % query_option))
    # 단체 성별
    sql.append(text("""
        SELECT CONCAT('단체 ', CASE WHEN `sex` = 'M' THEN '남' WHEN `sex` = 'F' THEN '여' END) as `name`, COUNT(*) AS `cnt`, COUNT(`amount`) AS `r_cnt`, SUM(`attend_yn`) AS `a_cnt`
        FROM `member` `m` LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `g`.`name` IS NOT NULL GROUP BY `sex`
    """ % query_option))

    query_params = {'camp_idx': camp_idx}

    stat = {
        'summary':[], 'area':[], 'persontype':[], 'group_name':[], 'campus': [],
        'training':[], 'job': [], 'ages': []
    }
    for s in sql:
        results = db.session.execute(s, query_params)
        for r in results:
            stat['summary'].append(dict(r))

    # 지부별
    query = text("""
        SELECT `a`.`idx` `idx`, `a`.`idx` `param`, `a`.`name` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `area` `a` ON `m`.`area_idx` = `a`.`idx` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `cancel_yn` = 0 GROUP BY `a`.`name`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['area'].append(dict(r))

    # 참가구분별
    query = text("""
        SELECT `m`.`persontype` `name`, `m`.`persontype` `param`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `cancel_yn` = 0 GROUP BY `persontype`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['persontype'].append(dict(r))

    # 단체별
    query = text("""
        SELECT `g`.`idx` `idx`, `g`.`idx` `param`, `g`.`name` `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `group` `g` ON `m`.`group_idx` = `g`.`idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 GROUP BY `g`.`idx` ORDER BY `g`.`name`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['group_name'].append(dict(r))

    # 캠퍼스별
    query = text("""
        SELECT `ms`.`value` `name`, `ms`.`value` `param`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'campus' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['campus'].append(dict(r))

    # 인터콥훈련여부별
    query = text("""
        SELECT `ms`.`value` `name`, `ms`.`value` `param`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'training' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['training'].append(dict(r))

    # 직업/직군별
    query = text("""
        SELECT `ms`.`value` `name`, `ms`.`value` `param`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
        LEFT JOIN `membership` `ms` ON `ms`.`member_idx` = `m`.`idx`
        WHERE (`m`.`camp_idx` = :camp_idx %s) AND `m`.`cancel_yn` = 0 AND `ms`.`key` = 'job' GROUP BY `ms`.`value`
    """ % query_option)

    results = db.session.execute(query, query_params)
    for r in results:
        stat['job'].append(dict(r))

    camp = db.select_one("SELECT * FROM `camp` WHERE `idx` = :camp_idx", query_params)
    year = camp['year']

    # 연령별 통계
    query = text("""
        SELECT CONCAT(`ages`,'대') `name`, COUNT(*) `cnt`, COUNT(`amount`) `r_cnt`, SUM(`attend_yn`) `a_cnt`
        FROM (
            SELECT LEFT(%s-(MID(`m`.`birth`,1,4)),1)*10 AS `ages`, `p`.`amount` `amount`, `m`.`attend_yn` `attend_yn`
            FROM `member` `m` LEFT JOIN `payment` `p` ON `m`.`idx` = `p`.`member_idx`
            WHERE (`camp_idx` = :camp_idx %s) AND `cancel_yn` = 0
        ) `mem`
        GROUP BY `mem`.`ages`
    """ % (year, query_option))

    results = db.session.execute(query, query_params)
    for r in results:
        stat['ages'].append(dict(r))

    return stat
