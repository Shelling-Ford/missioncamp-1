/*global $, document, alert */
$(document).ready(function () {
    'use strict';

    if ( $('input[name=persontype]:checked').val() === '스탭' ) {
        $('.stafftype').show();
    } else {
    	$('.stafftype').hide();
    }
    
    if ( $('input[name=persontype]:checked').val() === '어린이') {
    	$('.school').show();
    } else {
    	$('.school').hide();
    }
    

    $('input[name=persontype]').change(function () {
        if ($(this).val() === '스탭') {
            $('.stafftype').show();
        } else {
        	$('.stafftype').hide();
        }
        
        if ($(this).val() === '어린이') {
        	$('.school').show();
        } else {
        	$('.school').hide();
        }
        
    });
    
    
});



// 폼 검증 함수
function validate_form() {
    
    'use strict';
    // 이메일 중복검사
    if (!validator.validate_userid('아이디')) {
        return false;
    }
    
    // 비밀번호 필드가 존재할 경우(단체 멤버일 경우에는 없음)
    if (!validator.validate_pwd()) {
        return false;
    }
    
    // 이름 입력 안함
    if (!validator.validate_text('name', '이름을 입력해 주세요')) {
        return false;
    }
    
    // 지부 선택 안함
    if (!validator.validate_selected('area_idx', '지부를 선택해 주세요')) {
        return false;
    }
    
    // 성별 선택 안함
    if (!validator.validate_checked('sex', '성별을 선택해 주세요')) {
        return false;
    }
    
    
    
    // 생년월일
    if (!validator.validate_text('birth', '생년월일을 입력해 주세요')) {
        return false;
    }
    
    // 연락처
    if (!validator.validate_contact()) {
        return false;
    }
    
    // 소속교회
    if (!validator.validate_text('church', '소속 교회를 입력해 주세요')) {
        return false;
    }
    
    // 참가 구분
    if (!validator.validate_checked('persontype', '참가구분을 선택해 주세요')) {
        return false;
    }
    
    // 스탭구분 선택 안함 
    if ( $('input[name=persontype]:checked').val() === '스탭' ) {
    	if (!validator.validate_checked('stafftype', '스탭구분을 선택해 주세요')) {
            return false;
        }
    }
    
    // 단체버스
    if (!validator.validate_checked('bus_yn', '단체버스 이용 여부를 선택해 주세요')) {
        return false;
    }
    
    
    // 뉴커머 여부
    if (!validator.validate_checked('newcomer_yn', '선캠 처음 참석 여부를 선택해 주세요')) {
        return false;
    }
    
    // 인터콥 훈련 여부
    if (!validator.validate_training()) {
        return false;
    }
    
    return true;
}

function submit_form() {
    'use strict';
    if (validate_form()) {
        $('#form').submit();
    }
}