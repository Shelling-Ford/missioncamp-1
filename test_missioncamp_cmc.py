'''청년대학생 선교캠프 단위 테스트'''
import unittest
from core.database import DB as db
from core.models import Member, Membership, Payment, Camp, Group
from missioncamp.app import APP as app


CMC_CAMP_IDX = Camp.get_idx('cmc')

INDIVIDUAL_SAMPLE_DATA = dict(
    userid="test123@test.tst",
    pwd="123",
    pwd2="123",
    name="123",
    area_idx="1",
    sex="M",
    birth="1988",
    hp="010",
    hp2="1234",
    hp3="1234",
    contact="010-1234-1234",
    church="123",
    persontype="청년",
    bus_yn="1",
    mit_yn="1",
    fullcamp_yn="1",
    newcomer_yn="0",
    vision_yn="1",
    training=["비전스쿨", "선교캠프"],
    language="",
    memo=""
)

INDIVIDUAL_EDIT_DATA = dict(
    pwd="456",
    pwd2="456",
    name="123",
    area_idx="1",
    sex="M",
    birth="1988",
    hp="010",
    hp2="1234",
    hp3="1234",
    contact="010-1234-1234",
    church="123",
    persontype="청년",
    bus_yn="1",
    mit_yn="1",
    fullcamp_yn="1",
    newcomer_yn="0",
    vision_yn="1",
    training=["비전스쿨", "선교캠프"],
    language="",
    memo=""
)

GROUP_SAMPLE_DATA = dict(
    groupid="test8870",
    pwd="1234",
    pwd2="1234",
    name="test",
    leadername="test leader",
    leadercontact="010-1111-1122",
    leaderjob="no",
    area_idx="1",
    memo="test memo"
)

GROUP_EDIT_DATA = dict(
    pwd="345",
    pwd2="345",
    name="test",
    leadername="test leader",
    leadercontact="010-1111-1122",
    leaderjob="no",
    area_idx="1",
    memo="test memo"
)


def delete_member(userid, camp_idx):
    '''
    신청자 정보 삭제;
    param: userid, camp_idx
    return: None
    '''
    members = db.session.query(Member).filter(Member.userid == userid, Member.camp_idx == camp_idx).all()

    for member in members:
        memberships = db.session.query(Membership).filter(Membership.member_idx == member.idx).all()
        for membership in memberships:
            db.session.delete(membership)

        payment = db.session.query(Payment).filter(Payment.member_idx == member.idx).first()
        if payment is not None:
            db.session.delete(payment)

        db.session.delete(member)
    db.session.commit()


def delete_group(groupid, camp_idx):
    '''
    신청 단체 정보 삭제;
    :param: groupid, camp_idx
    :return: None
    '''
    group = db.session.query(Group).filter(Group.groupid == groupid, Group.camp_idx == camp_idx).one()
    member_list = db.session.query(Member).filter(Member.group_idx == group.idx).all()
    for member in member_list:
        delete_member(member.userid, member.camp_idx)

    db.session.delete(group)
    db.session.commit()


class MissioncampCmcTestCase(unittest.TestCase):
    '''청대선캠 테스트 케이스'''
    def setUp(self):
        '''테스트 전 실행'''
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        '''테스트 종료 후 실행'''
        # delete_member(INDIVIDUAL_SAMPLE_DATA['userid'], CMC_CAMP_IDX)
        pass

    def reg_individual(self, data):
        '''개인신청'''
        return self.app.post("/cmc/registration", data=data, follow_redirects=True)

    def edit_individual(self, data):
        '''개인신청수정'''
        return self.app.post("/cmc/registration/edit", data=data, follow_redirects=True)

    def cancel_individual(self):
        '''개인신청취소'''
        return self.app.post("/cmc/registration/cancel", data=dict(
            cancel_reason="테스트"
        ), follow_redirects=True)

    def check_individual(self, userid, pwd, logintype):
        '''개인신청 조회'''
        return self.app.post("/cmc/login", data=dict(
            userid=userid,
            pwd=pwd,
            logintype=logintype
        ), follow_redirects=True)

    def reg_group(self, data):
        '''단체 신청'''
        result = self.app.post("/cmc/group/registration", data=data, follow_redirects=True)

        assert "신청이 완료되었습니다." in result.data.decode('utf-8')

    def edit_group(self, data):
        '''단체수정'''
        result = self.app.post("/cmc/group/edit", data=data, follow_redirects=True)
        assert "단체 정보 수정이 완료되었습니다." in result.data.decode('utf-8')

    # 테스트 항목;
    '''
        1. 개인신청 신청-조회-수정-조회-신청(중복오류)-취소-조회(오류)-신청-삭제;
        2. 단체신청;

        단체;
        1. 신청-조회-취소-삭제;
        2. 신청-조회-수정-조회-삭제;
        3. 신청-조회-멤버추가-삭제;
        4. 신청-조회-멤버추가-멤버취소-삭제;
    '''

    def test_1(self):
        '''테스트1: 개인신청 신청-조회-수정-조회-신청(중복오류)-취소-조회(오류)-신청-조회-삭제'''

        # 신청;
        result = self.reg_individual(INDIVIDUAL_SAMPLE_DATA)
        assert '신청이 완료되었습니다.' in result.data.decode('utf-8')

        try:
            # 조회;
            result = self.check_individual(INDIVIDUAL_SAMPLE_DATA['userid'], INDIVIDUAL_SAMPLE_DATA['pwd'], '개인')
            assert '아이디 또는 비밀번호가 잘못되었습니다.' not in result.data.decode('utf-8')
            assert '신청 구분을 선택해주세요' not in result.data.decode('utf-8')
            assert '아이디를 입력해주세요' not in result.data.decode('utf-8')
            assert '비밀번호를 입력해 주세요' not in result.data.decode('utf-8')
            assert '개인 신청 조회' in result.data.decode('utf-8')

            # 수정;
            result = self.edit_individual(INDIVIDUAL_EDIT_DATA)
            assert '수정이 완료되었습니다' in result.data.decode('utf-8')

            # 조회;
            result = self.check_individual(INDIVIDUAL_SAMPLE_DATA['userid'], INDIVIDUAL_EDIT_DATA['pwd'], '개인')
            assert '아이디 또는 비밀번호가 잘못되었습니다.' not in result.data.decode('utf-8')
            assert '신청 구분을 선택해주세요' not in result.data.decode('utf-8')
            assert '아이디를 입력해주세요' not in result.data.decode('utf-8')
            assert '비밀번호를 입력해 주세요' not in result.data.decode('utf-8')
            assert '개인 신청 조회' in result.data.decode('utf-8')

            # 신청(중복오류)

            # 취소;
            result = self.cancel_individual()
            assert '신청이 취소되었습니다' in result.data.decode('utf-8')

            # 조회(오류)
            result = self.check_individual(INDIVIDUAL_SAMPLE_DATA['userid'], INDIVIDUAL_EDIT_DATA['pwd'], '개인')
            assert '아이디 또는 비밀번호가 잘못되었습니다.' in result.data.decode('utf-8')
            assert '신청 구분을 선택해주세요' not in result.data.decode('utf-8')
            assert '아이디를 입력해주세요' not in result.data.decode('utf-8')
            assert '비밀번호를 입력해 주세요' not in result.data.decode('utf-8')

            # 신청;
            result = self.reg_individual(INDIVIDUAL_SAMPLE_DATA)
            assert '신청이 완료되었습니다.' in result.data.decode('utf-8')

            # 조회;
            result = self.check_individual(INDIVIDUAL_SAMPLE_DATA['userid'], INDIVIDUAL_SAMPLE_DATA['pwd'], '개인')
            assert '아이디 또는 비밀번호가 잘못되었습니다.' not in result.data.decode('utf-8')
            assert '신청 구분을 선택해주세요' not in result.data.decode('utf-8')
            assert '아이디를 입력해주세요' not in result.data.decode('utf-8')
            assert '비밀번호를 입력해 주세요' not in result.data.decode('utf-8')
            assert '개인 신청 조회' in result.data.decode('utf-8')

        finally:
            # 삭제;
            delete_member(INDIVIDUAL_SAMPLE_DATA['userid'], CMC_CAMP_IDX)


if __name__ == "__main__":
    unittest.main()
