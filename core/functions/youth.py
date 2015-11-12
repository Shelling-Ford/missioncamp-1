#-*-coding:utf-8-*-
from core.functions import regIndividualCommon
from core.functions import editIndividualCommon
import datetime

# 개인 신청 등록
def regIndividual(camp_idx, formData, group_idx=None):
    membership_data_list = getMembershipDataList(camp_idx, formData)
    member_idx = regIndividualCommon(camp_idx, formData, membership_data_list, group_idx)
    return member_idx

# 개인신청 수정
def editIndividual(camp_idx, member_idx, formData, group_idx=None):
    membership_data_list = getMembershipDataList(camp_idx, formData)
    editIndividualCommon(camp_idx, member_idx, formData, membership_data_list, group_idx)

def getMembershipDataList(camp_idx, formData):
    membership_data_list = []

    if formData['group_idx'] is None:
        membership_data_list.append({'camp_idx':camp_idx, 'key':'email', 'value':formData['email']})

        if formData['persontype'] == u'중학생' or formData['persontype'] == u'고등학생':
            membership_data_list.append({'camp_idx':camp_idx, 'key':'sch1', 'value':formData['sch1']})
            membership_data_list.append({'camp_idx':camp_idx, 'key':'sch2', 'value':formData['sch2']})

    if 'training' in formData:
        for t in formData['training']:
            membership_data_list.append({'camp_idx':camp_idx, 'key':'training', 'value':t})

    if 'route' in formData:
        for t in formData['route']:
            membership_data_list.append({'camp_idx':camp_idx, 'key':'route', 'value':t})

    return membership_data_list
