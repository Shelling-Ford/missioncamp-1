/*global $, document, alert, validator */


// 폼 검증 함수
function validate_form() {
    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/i, contact = $('#contact').val();
    var group_idx = $('input[name=group_idx]').val()

    // 이름 입력 안함
    if ($('#name').val() === '') {
        alert('이름을 입력해 주세요');
        return false;
    }

    // 성별 선택 안함
    if ($('input[name=sex]:checked').val() === undefined) {
        alert('성별을 선택해 주세요');
        return false;
    }

    //출생년도 선택 안함
    if ($('#birth').val() === '') {
        alert('출생년도를 선택해 주세요');
        return false;
    }

    // 연락처
    if (!contact_regex.test(contact)) {
        alert('올바른 연락처 정보를 입력해 주세요');
        return false;
    }

    // 참가 구분
    if ($('input[name=persontype]:checked').val() === undefined) {
        alert('참가구분을 선택해 주세요');
        return false;
    }

    // 뉴커머 여부
    if ($('input[name=newcomer_yn]:checked').val() === undefined) {
        alert('선캠 처음 참석 여부를 선택해 주세요');
        return false;
    }

    if ($('input[type=checkbox]:checked').val() === undefined) {
        alert('인터콥 훈련여부를 적어도 하나 이상 체크해 주세요');
        return false;
    }

    $('#contact').val(contact);

    return true;
}

function submit_form() {
    'use strict';
    if (validate_form()) {
        $('#form').submit();
    }
}
