#-*-coding:utf-8-*-
from core import functions as core_functions
from core.database import db
import datetime
from sqlalchemy.sql import text

# 개인 신청 등록
def regIndividual(camp_idx, formData, group_idx=None):
    formData['camp_idx'] = camp_idx
    formData['attend_yn'] = 0
    formData['group_idx'] = group_idx
    formData['regdate'] = datetime.datetime.today()

    attend = core_functions.getAttendArray(camp_idx, formData)
    formData['attend1'] = attend[0]
    formData['attend2'] = attend[1]
    formData['attend3'] = attend[2]
    formData['attend4'] = attend[3]

    insert_sql = text("""
        INSERT INTO `member`(camp_idx, userid, pwd, name, area_idx, contact,
            church, birth, sex, bus_yn, mit_yn, newcomer_yn, persontype,
            fullcamp_yn, date_of_arrival, date_of_leave, language, group_idx, regdate, memo, attend1, attend2, attend3, attend4)
        VALUES (:camp_idx, :userid, :pwd, :name, :area_idx,
            :contact, :church, :birth, :sex, :bus_yn, :mit_yn,
            :newcomer_yn, :persontype, :fullcamp_yn,
            :date_of_arrival, :date_of_leave, :language, :group_idx,
            :regdate, :memo, :attend1, :attend2, :attend3, :attend4)
    """)

    db.raw_query(insert_sql, formData)

    lastrowid = db.execute("SELECT LAST_INSERT_ID() as idx")
    member_idx = lastrowid[0]['idx']

    insertMembershipData(camp_idx, member_idx, formData)

    db.commit()
    return member_idx

# 개인신청 수정
def editIndividual(camp_idx, member_idx, formData, group_idx=None):
    formData['member_idx'] = member_idx
    formData['group_idx'] = group_idx

    # 비밀번호 항목이 빈칸인 경우 비밀번호를 지우지 않도록 함.
    if formData['pwd'] == '' or formData['pwd'] == None:
        pwd = db.execute('SELECT `pwd` FROM `member` WHERE `idx` = :idx', {'idx': member_idx})[0]['pwd']
        formData['pwd'] = pwd

    attend = core_functions.getAttendArray(camp_idx, formData)
    formData['attend1'] = attend[0]
    formData['attend2'] = attend[1]
    formData['attend3'] = attend[2]
    formData['attend4'] = attend[3]

    update_sql = text("""
        UPDATE `member` SET
            `name` = :name, `pwd` = :pwd, `area_idx` = :area_idx, `contact` = :contact,
            `church` = :church, `birth` = :birth, `sex` = :sex,
            `bus_yn` = :bus_yn, `mit_yn` = :mit_yn,
            `newcomer_yn` = :newcomer_yn, `persontype` = :persontype,
            `fullcamp_yn` = :fullcamp_yn, `date_of_arrival` = :date_of_arrival,
            `date_of_leave` = :date_of_leave, `language` = :language,
            `group_idx` = :group_idx, `memo` = :memo,
            `attend1` = :attend1, `attend2` = :attend2, `attend3` = :attend3, `attend4` = :attend4
        WHERE
            `idx` = :member_idx
    """)

    db.raw_query(update_sql, formData)
    db.raw_query("DELETE FROM `membership` WHERE `member_idx` = :member_idx", {'member_idx': member_idx})

    insertMembershipData(camp_idx, member_idx, formData)

    db.commit()

# 최초 신청서 작성과 신청서 수정에서 공통적으로 사용되는 부분을 모듈화함.
def insertMembershipData(camp_idx, member_idx, formData):
    membership_insert = "INSERT INTO `membership`(`camp_idx`, `member_idx`, `key`, `value`) VALUES (:camp_idx, :member_idx, :key, :value)"
    if formData['persontype'] == u'청년':
        membership_data = {'camp_idx':camp_idx, 'member_idx':member_idx, 'key':'job', 'value':formData['job']}
        db.raw_query(membership_insert, membership_data)

    for t in formData['training']:
        membership_data = {'camp_idx':camp_idx, 'member_idx':member_idx, 'key':'training', 'value':t}
        db.raw_query(membership_insert, membership_data)
