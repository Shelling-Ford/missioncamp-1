#-*-coding:utf-8-*-
from core.database import db

from flask import request
from sqlalchemy.sql import text
import datetime
import hashlib

# 파라메터: 캠프 코드값
# 반환값: global_options 테이블에 등록되어있는 년도와 학기, 그리고 파라메터로 넘겨준 캠프 코드에 맞는 캠프 idx
def getCampIdx(camp, year=None, term=None):
    if year is None:
        year = db.execute("SELECT `value` FROM `global_options` WHERE `key` = 'current_year'")[0]['value']
    if term is None:
        term = db.execute("SELECT `value` FROM `global_options` WHERE `key` = 'current_term'")[0]['value']
    camp_idx = db.execute("SELECT `idx` FROM `camp` WHERE `code` = '%s' AND `year` = %s AND `term` = %s" % (camp, year, term))[0]['idx']
    return camp_idx

# 파라메터: 캠프 고유번호, 옵션 키
# 반환값: 옵션 값
def getCampOption(camp_idx, option_key):
    option_data = db.execute("SELECT `value` FROM `options` WHERE `key` = '%s' AND `camp_idx` = %s" % (option_key, cmap_idx))[0]['value']
    return option_data

# 파라메터: 캠프 고유번호
# 반환값: 캠프 날자 리스트
def getCampDateList(camp_idx):
    campdata = db.execute("SELECT `startday`, `campday` FROM `camp` WHERE `idx` = %s" % camp_idx)[0]
    datelist = []
    for i in range(campdata['campday']):
        datelist.append(campdata['startday'] + datetime.timedelta(days=(i-1)))

    return datelist

# 지부 목록
def getAreaList(camp):
    arealist = db.execute("SELECT * FROM `area` WHERE `camp` = '*' OR `camp` LIKE '%s' ORDER BY `type` ASC, `name` ASC" % ('%' + camp + '%',))
    return arealist

# 지부 고유번호를 지부 이름으로 변환
def getAreaName(area_idx):
    area_name = db.execute("SELECT `name` FROM `area` WHERE `idx` = %s" % (area_idx,))[0]['name']
    return area_name

# 생년월일
def getDateSelectList():
    date_select_list = {}
    # 연도 리스트를 생성, 1900년 부터 2015년 까지
    date_select_list['yr_list'] = [ i for i in range(2015, 1900, -1) ]
    # 월 리스트를 생성 1월 부터 12월 까지
    date_select_list['m_list'] = [ '%02d' % i for i in range(1, 13) ]
    # 일 리스트를 생성 1일 부터 31일 까지
    date_select_list['d_list'] = [ '%02d' % i for i in range(1, 32) ]

    return date_select_list

# 개인신청 아이디 중복검사
def checkUserId(campidx, userid):
    return db.execute("SELECT COUNT(`idx`) as `cnt` FROM `member` WHERE `camp_idx` = %s AND `userid` = '%s' AND `cancel_yn` = 0" % (campidx, userid))[0]['cnt']

# 단체 아이디 중복 검사
def checkGroupId(campidx, groupid):
    return db.execute("SELECT COUNT(`idx`) as `cnt` FROM `group` WHERE `camp_idx` = %s AND `groupid` = '%s' AND `cancel_yn` = 0" % (campidx, groupid))[0]['cnt']


# 개인 신청조회 로그인 체크
def loginCheckUserid(campidx, userid, pwd):
    cnt = db.execute("SELECT COUNT(`idx`) as `cnt` FROM `member` WHERE `camp_idx` = %s AND `userid` = '%s' AND `pwd` = '%s' AND `cancel_yn` = 0" % (campidx, userid, hashlib.sha224(pwd).hexdigest()))[0]['cnt']
    return True if cnt > 0 else False

# 개인신청자 일련번호 반환
def getUserIdx(campidx, userid):
    return db.execute("SELECT `idx` FROM `member` WHERE `camp_idx` = %s AND `userid` = '%s'" % (campidx, userid))[0]['idx']

# 단체 신정조회 로그인 체크
def loginCheckGroupid(campidx, groupid, pwd):
    cnt = db.execute("SELECT COUNT(`idx`) as `cnt` FROM `group` WHERE `camp_idx` = %s AND `groupid` = '%s' AND `pwd` = '%s' AND `cancel_yn` = 0" % (campidx, groupid, hashlib.sha224(pwd).hexdigest()))[0]['cnt']
    return True if cnt > 0 else False

# 단체 일련번호 조회
def getGroupIdx(campidx, groupid):
    return db.execute("SELECT `idx` FROM `group` WHERE `camp_idx` = %s AND `groupid` = '%s'" % (campidx, groupid))[0]['idx']

# 멤버십 리스트를 딕셔너리로 변환
def getMembership(membership_list):
    membership = {'training':[]}
    for m in membership_list:
        if m['key'] == 'training':
            membership[m['key']].append(m['value'])
        else:
            membership[m['key']] = m['value']
    return membership

# 개인신청시 필수항목
individual_form_keys = [
    'userid', 'pwd', 'name', 'area_idx', 'contact', 'church', 'birth', 'sex',
    'bus_yn', 'mit_yn', 'newcomer_yn', 'persontype', 'fullcamp_yn',
    'date_of_arrival', 'date_of_leave', 'language', 'memo'
]

# 단체신청시 필수 항목
group_form_keys = [
    'name', 'groupid', 'pwd', 'leadername', 'leadercontact', 'leaderjob',
    'grouptype', 'area_idx', 'memo'
]

# key 오류가 발생하지 않도록 등록 필수항목인 key의 값을 None으로 셋팅해줌.
def getSafeFormData(formData, keys):
    for key in keys:
        if not key in formData:
            formData[key] = None
    return formData

# request로부터 제출된 양식 데이터를 가져옴
def getFormData():
    formData = {}
    for key in request.form.keys():
        if key == 'pwd':
            pwd = request.form.get(key, None)
            if pwd != '' and pwd != None:
                formData[key] = hashlib.sha224(pwd).hexdigest()
            else:
                formData[key] = None
        elif key == 'training' or key == 'route':
            formData[key] = request.form.getlist(key, None)
        else:
            s = request.form.get(key, None)
            formData[key] = s.strip()
    return formData

# add 또는 edit 시에 넘겨주는 form data를 dictionary 타입으로 반환해준다.
# regIndividual함수와 editIndividual함수에서 이 함수를 사용함
def getIndividualFormData():
    formData = getSafeFormData(getFormData(), individual_form_keys)
    return formData

def getGroupFormData():
    formData = getSafeFormData(getFormData(), group_form_keys)
    return formData

def getAttendArray(camp_idx, formData):
    attend = [0, 0, 0, 0]

    campdata = db.select_one("SELECT `startday`, `campday` FROM `camp` WHERE `idx` = :idx", {'idx':camp_idx})

    date_of_arrival = formData['date_of_arrival']
    date_of_leave = formData['date_of_leave']

    # date_of_arrival 변수와 date_of_leave 변수를 이용해 attend1, attend2, attend3, attend4 계산, 어드민 통계에 활용됨
    if campdata['campday'] == 4:
        if date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday']):
            attend[0] = 1
        elif date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=1)):
            attend[0] = 1
            attend[1] = 1
        elif date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[0] = 1
            attend[1] = 1
            attend[2] = 1
        elif date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=3)):
            attend[0] = 1
            attend[1] = 1
            attend[2] = 1
            attend[3] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=1)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=1)):
            attend[1] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=1)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[1] = 1
            attend[2] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=1)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=3)):
            attend[1] = 1
            attend[2] = 1
            attend[3] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=2)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[2] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=2)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=3)):
            attend[2] = 1
            attend[3] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=3)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=3)):
            attend[3] = 1
    elif campdata['campday'] == 3:
        if date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday']):
            attend[0] = 1
        elif date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=1)):
            attend[0] = 1
            attend[1] = 1
        elif date_of_arrival == str(campdata['startday']) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[0] = 1
            attend[1] = 1
            attend[2] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=1)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=1)):
            attend[1] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=1)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[1] = 1
            attend[2] = 1
        elif date_of_arrival == str(campdata['startday'] + datetime.timedelta(days=2)) and date_of_leave == str(campdata['startday'] + datetime.timedelta(days=2)):
            attend[2] = 1
    return attend

#개인신청 입력
def regIndividualCommon(camp_idx, formData, membershipDataList, group_idx=None):
    formData['camp_idx'] = camp_idx
    formData['attend_yn'] = 0
    formData['group_idx'] = group_idx
    formData['regdate'] = datetime.datetime.today()

    attend = getAttendArray(camp_idx, formData)
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

    membership_insert = text("INSERT INTO `membership`(`camp_idx`, `member_idx`, `key`, `value`) VALUES (:camp_idx, %s, :key, :value)" % member_idx)
    for membership_data in membershipDataList:
        db.raw_query(membership_insert, membership_data)

    db.commit()
    return member_idx

#개인신청 수정
def editIndividualCommon(camp_idx, member_idx, formData, membershipDataList, group_idx=None):
    formData['member_idx'] = member_idx

    # 크로스에서 단체 멤버를 수정할 경우 개인으로 바꾸는 오류 수정 2015-11-20
    if 'group_idx' not in formData or formData['group_idx'] is None:
        formData['group_idx'] = group_idx

    # 비밀번호 항목이 빈칸인 경우 비밀번호를 지우지 않도록 함.
    if formData['pwd'] == '' or formData['pwd'] == None:
        pwd = db.execute('SELECT `pwd` FROM `member` WHERE `idx` = :idx', {'idx': member_idx})[0]['pwd']
        formData['pwd'] = pwd

    attend = getAttendArray(camp_idx, formData)
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

    membership_insert = text("INSERT INTO `membership`(`camp_idx`, `member_idx`, `key`, `value`) VALUES (:camp_idx, %s, :key, :value)" %member_idx)
    for membership_data in membershipDataList:
        db.raw_query(membership_insert, membership_data)

    db.commit()

# 개인신청 취소
def cancelIndividual(member_idx, reason):
    cancel_data = (reason, datetime.datetime.today(), member_idx)
    db.raw_query("UPDATE `member` SET `cancel_yn` = 1, `cancel_reason` = '%s', `canceldate` = '%s' WHERE `idx` = %s" % cancel_data)
    db.commit()

# 개인신청자 조회하기
def getIndividualData(member_idx):
    member = db.execute("SELECT * FROM `member` WHERE `idx` = %s" % (member_idx,))[0]
    member['membership'] = getMembership(db.execute("SELECT * FROM `membership` WHERE `member_idx` = %s" % (member_idx,)))
    return member

# 개인 신청자 정보 삭제
def deleteIndividual(member_idx):
    db.raw_query("DELETE FROM `payment` WHERE `member_idx` = %s" % (member_idx,))
    db.raw_query("DELETE FROM `membership` WHERE `member_idx` = %s" % (member_idx,))
    db.raw_query("DELETE FROM `member` WHERE `member_idx` = %s" % (member_idx,))
    db.commit()

# 단체 신청
def regGroup(camp_idx, formData):
    formData['camp_idx'] = camp_idx
    formData['regdate'] = datetime.datetime.today()

    db.raw_query("""
        INSERT INTO `group`(`camp_idx`, `name`, `groupid`, `pwd`, `leadername`,
            `leadercontact`, `leaderjob`, `area_idx`, `mem_num`, `cancel_yn`, `grouptype`, `regdate`, `memo`)
        VALUES (%(camp_idx)s, '%(name)s', '%(groupid)s', '%(pwd)s', '%(leadername)s',
            '%(leadercontact)s', '%(leaderjob)s', %(area_idx)s, 0, 0, '%(grouptype)s', '%(regdate)s', '%(memo)s'
        )
    """ % formData)
    group_idx = db.execute("SELECT LAST_INSERT_ID() as idx")[0]['idx']
    db.commit()

    return group_idx

#단체신청 수정
def editGroup(group_idx, formData):
    formData['group_idx'] = group_idx

    # 비밀번호 항목이 빈칸인 경우 비밀번호를 지우지 않도록 함.
    if formData['pwd'] == '' or formData['pwd'] == None:
        formData['pwd'] = db.execute("SELECT `pwd` FROM `group` WHERE `idx` = %s" % (group_idx,))[0]['pwd']

    db.raw_query("""
        UPDATE `group` SET
            `name` = '%(name)s', `pwd` = '%(pwd)s', `leadername` = '%(leadername)s', `leadercontact` = '%(leadercontact)s',
            `leaderjob` = '%(leaderjob)s', `area_idx` = %(area_idx)s,
            `grouptype` = '%(grouptype)s', `memo` = '%(memo)s'
        WHERE
            `idx` = %(group_idx)s
    """ % formData)
    db.commit()

# 단체 조회하기
def getGroupData(group_idx):
    return db.execute("SELECT * FROM `group` WHERE `idx` = %s" % (group_idx,))[0]

def getMemberList(group_idx):
    member_list = db.execute("SELECT * FROM `member` WHERE `group_idx` = %s AND `cancel_yn` = 0" % (group_idx))
    for member in member_list:
        member['membership'] = getMembership(db.execute("SELECT * FROM `membership` WHERE `member_idx`= %s" % member['idx']))

    return member_list

# 단체 mem_num 증가
def inc_mem_num(group_idx):
    db.raw_query("UPDATE `group` SET mem_num = mem_num + 1 WHERE `idx` = %s" % (group_idx))
    db.commit()

# 단체 mem_num 감소
def dec_mem_num(group_idx):
    db.raw_query("UPDATE `group` SET mem_num = mem_num - 1 WHERE `idx` = %s AND mem_num > 0" % (group_idx))
    db.commit()

# 단체신청 취소
def cancelGroup(group_idx, reason):
    cancel_data = (reason, datetime.datetime.today(), group_idx)
    db.raw_query("UPDATE `member` SET `cancel_yn` = 1, `cancel_reason` = '%s', `canceldate` = '%s' WHERE `group_idx` = %s" % cancel_data)
    db.raw_query("UPDATE `group` SET `cancel_yn` = 1, `cancel_reason` = '%s', `canceldate` = '%s' WHERE `idx` = %s" % cancel_data)
    db.commit()
