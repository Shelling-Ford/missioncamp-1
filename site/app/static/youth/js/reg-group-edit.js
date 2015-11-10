/*global $, document, alert */

// 폼 검증 함수
function validate_form() {

    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, contact = $('#leadercontact').val();

    // 비밀번호 공백
    if ($('#pwd').val() !== '') {
        // 비밀번호 일치여부
        if ($('#pwd').val() !== $('#pwd2').val()) {
            alert('비밀번호가 일치하지 않습니다');
            return false;
        }
    }

    // 단체 이름 입력 안함
    if ($('#name').val() === '') {
        alert('단체 이름을 입력해 주세요');
        return false;
    }

    // 담당자 이름 입력 안함
    if ($('#leadername').val() === '') {
        alert('담당자 이름을 입력해 주세요');
        return false;
    }

    // 연락처
    if (!contact_regex.test(contact)) {
        alert('올바른 연락처 정보를 입력해 주세요');
        return false;
    }

    // 지부
    if ($('#area_idx').val() === '') {
        alert('지부를 선택해주세요');
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
