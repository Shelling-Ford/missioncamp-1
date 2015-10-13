#-*-coding:utf-8-*-
from core import functions as core_functions
import core.database as db
from contextlib import closing
import datetime

# 개인 신청 등록
def regIndividual(camp_idx, formData, group_idx=None):
    formData['camp_idx'] = camp_idx
    formData['attend_yn'] = 0
    formData['group_idx'] = group_idx
    formData['regdate'] = datetime.datetime.today()

    with closing(db.getConnection()) as conn:
        with closing(db.getCursor(conn)) as cursor:
            cursor.execute("""
                INSERT INTO `member`(camp_idx, userid, pwd, name, area_idx, contact,
                    church, birth, sex, bus_yn, mit_yn, attend_yn, newcomer_yn, persontype,
                    fullcamp_yn, date_of_arrival, date_of_leave, language, group_idx, regdate, memo)
                VALUES (%(camp_idx)s, %(userid)s, %(pwd)s, %(name)s, %(area_idx)s,
                    %(contact)s, %(church)s, %(birth)s, %(sex)s, %(bus_yn)s, %(mit_yn)s,
                    %(attend_yn)s, %(newcomer_yn)s, %(persontype)s, %(fullcamp_yn)s,
                    %(date_of_arrival)s, %(date_of_leave)s, %(language)s, %(group_idx)s, %(regdate)s, %(memo)s)
            """, formData)
            # 방금 추가한 신청자의 member_idx를 다시 불러옴
            member_idx = cursor.lastrowid

            membership_insert = 'INSERT INTO `membership`(`camp_idx`, `member_idx`, `key`, `value`) VALUES (%s, %s, %s, %s)'
            if formData['persontype'] == u'청년':
                membership_data = (camp_idx, member_idx, 'job', formData['job'])
                cursor.execute(membership_insert, membership_data)

            for t in formData['training']:
                membership_data = (camp_idx, member_idx, 'training', t)
                cursor.execute(membership_insert, membership_data)
            # 현재까지 실행된 쿼리 내용을 커밋한다
            conn.commit()

# 개인신청 수정
def editIndividual(camp_idx, member_idx, formData, group_idx=None):
    formData['member_idx'] = member_idx
    formData['group_idx'] = group_idx

    # 비밀번호 항목이 빈칸인 경우 비밀번호를 지우지 않도록 함.
    with closing(db.getConnection()) as conn:
        with closing(db.getCursor(conn)) as cursor:
            if formData['pwd'] == '' or formData['pwd'] == None:
                cursor.execute('SELECT `pwd` FROM `member` WHERE `idx` = %s', (member_idx,))
                formData['pwd'] = cursor.fetchone()['pwd']

            cursor.execute("""
                UPDATE `member` SET
                    `name` = %(name)s, `pwd` = %(pwd)s, `area_idx` = %(area_idx)s, `contact` = %(contact)s,
                    `church` = %(church)s, `birth` = %(birth)s, `sex` = %(sex)s,
                    `bus_yn` = %(bus_yn)s, `mit_yn` = %(mit_yn)s,
                    `newcomer_yn` = %(newcomer_yn)s, `persontype` = %(persontype)s,
                    `fullcamp_yn` = %(fullcamp_yn)s, `date_of_arrival` = %(date_of_arrival)s,
                    `date_of_leave` = %(date_of_leave)s, `language` = %(language)s,
                    `group_idx` = %(group_idx)s, `memo` = %(memo)s
                WHERE
                    `idx` = %(member_idx)s
            """, formData)

            # membership 테이블의 수정은 member_idx가 일치하는 모든 row를 삭제한 뒤 다시 등록
            cursor.execute('DELETE FROM `membership` WHERE `member_idx` = %s', (member_idx,))

            membership_insert = 'INSERT INTO `membership`(`camp_idx`, `member_idx`, `key`, `value`) VALUES (%s, %s, %s, %s)'
            if formData['persontype'] == u'청년':
                membership_data = (camp_idx, member_idx, 'job', formData['job'])
                cursor.execute(membership_insert, membership_data)

            for t in formData['training']:
                membership_data = (camp_idx, member_idx, 'training', t)
                cursor.execute(membership_insert, membership_data)
            # 현재까지 실행된 쿼리 내용을 커밋한다
            conn.commit()
