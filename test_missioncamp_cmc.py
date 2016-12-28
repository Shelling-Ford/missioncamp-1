'''
청년대학생 선교캠프 단위 테스트
'''
import unittest
from core.database import DB as db
from core.models import Member, Membership, Payment, Camp
from missioncamp.app import APP as app


def delete_member(userid, camp_idx):
    '''
    신청자 정보 삭제;
    param: userid, camp_idx
    return: None
    '''
    member = db.session.query(Member).filter(Member.userid == userid, Member.camp_idx == camp_idx).one()
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
    pass


class MissioncampCmcTestCase(unittest.TestCase):
    '''청대선캠 테스트 케이스'''
    def setUp(self):
        '''테스트 전 실행'''
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.reg_individual()

    def tearDown(self):
        '''테스트 종료 후 실행'''
        # self.cancel_individual()
        delete_member("test123@test.tst", Camp.get_idx('cmc'))

    def reg_individual(self):
        '''개인신청 테스트'''
        result = self.app.post("/cmc/registration", data=dict(
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
        ), follow_redirects=True)
        assert '신청이 완료되었습니다.' in result.data.decode('utf-8')

    def reg_group(self):
        '''단체 신청 테스트'''
        result = self.app.post("/cmc/group/registration", data=dict(
            groupid="test8870",
            pwd="1234",
            pwd2="1234",
            name="test",
            leadername="test leader",
            leadercontact="010-1111-1122",
            leaderjob="no",
            area_idx="1",
            memo="test memo"
        ), follow_redirects=True)

        assert "신청이 완료되었습니다." in result.data.decode('utf-8')

    def edit_group(self):
        '''단체수정 테스트'''
        result = self.app.post("/cmc/group/edit", data=dict(
            pwd="345",
            pwd2="345",
            name="test",
            leadername="test leader",
            leadercontact="010-1111-1122",
            leaderjob="no",
            area_idx="1",
            memo="test memo"
        ), follow_redirects=True)
        assert "단체 정보 수정이 완료되었습니다." in result.data.decode('utf-8')


    def cancel_individual(self):
        '''신청취소'''
        result = self.app.post("/cmc/registration/cancel", data=dict(
            cancel_reason="테스트"
        ), follow_redirects=True)
        print(result.data.decode('utf-8'))
        assert '신청이 취소되었습니다' in result.data.decode('utf-8')

    def test_check_individual(self):
        '''개인신청 조회'''
        result = self.app.post("/cmc/login", data=dict(
            userid="test123@test.tst",
            pwd="123",
            logintype="개인"
        ), follow_redirects=True)
        assert '아이디 또는 비밀번호가 잘못되었습니다.' not in result.data.decode('utf-8')
        assert '신청 구분을 선택해주세요' not in result.data.decode('utf-8')
        assert '아이디를 입력해주세요' not in result.data.decode('utf-8')
        assert '비밀번호를 입력해 주세요' not in result.data.decode('utf-8')
        assert '개인 신청 조회' in result.data.decode('utf-8')


if __name__ == "__main__":
    unittest.main()
