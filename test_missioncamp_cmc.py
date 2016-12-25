'''
청년대학생 선교캠프 단위 테스트
'''
import unittest
from missioncamp import app as missioncamp


class MissioncampCmcTestCase(unittest.TestCase):
    '''청대선캠 테스트 케이스'''
    def setUp(self):
        missioncamp.APP.config['TESTING'] = True
        self.app = missioncamp.APP.test_client()
        self.reg_individual()

    def tearDown(self):
        self.cancel_individual()

    def reg_individual(self):
        '''
        개인신청
        '''
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
