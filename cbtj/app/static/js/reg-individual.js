/*global $, document, alert */
$(document).ready(function () {
    'use strict';
    $('#bubun').hide();
    $('#young_job').hide();

    // 참가구분 == 청년 일때 직업란 보여줌
    // 그 외는 모두 숨김
    $('input[name=persontype]').change(function () {
        if ($(this).val() === '청년') {
            $('#young_job').show();
        } else {
            $('#young_job').hide();
        }
    });

    // 참가형태 == 부분참가 일때 참가기간 선택 보여줌
    // 그 외는 모두 숨김
    $('input[name=fullcamp_yn]').change(function () {
        if ($(this).val() === '0') {
            $('#bubun').show();
        } else {
            $('#bubun').hide();
        }
    });

    $('.membership').change(function () {
        if ($('#none').is(':checked')) {
            $('#none').attr('checked', false);
        }
    });

    $('#none').change(function () {
        if ($('#none').is(':checked')) {
            $('.membership').attr('checked', false);
            $('#none').attr('checked', true);
        }
    });
});
var isChecked = false;

function check_userid() {
    'use strict';
    var userid = $('#userid').val(), campidx = $('#campidx').val(), email_regex = /^[0-9a-zA-Z]([\-_\.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([\-_\.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i;
    var camp = $('#camp').val();

    if (!email_regex.test(userid)) {
        alert('올바른 이메일이 아닙니다.');
        isChecked = false;
        return;
    }

    $.ajax({
        url: './check-userid',
        type: 'POST',
        data: 'userid=' + userid + '&campidx=' + campidx,
        success: function (data) {
            if (parseInt(data, 10) === 0) {
                alert("사용이 가능한 이메일입니다.");
                isChecked = true;
            } else {
                alert("사용이 불가한 이메일입니다.");
                isChecked = false;
            }
        }
    });
}



// 폼 검증 함수
function validate_form() {

    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, contact = $('#hp').val() + '-' + $('#hp2').val() + '-' + $('#hp3').val();

    // 이메일 중복검사
    if (!isChecked) {
        alert('이메일 중복 검사를 해주세요');
        return false;
    }

    // 비밀번호 필드가 존재할 경우(단체 멤버일 경우에는 없음)
    if($('#pwd').length) {
        // 비밀번호 공백
        if ($('#pwd').val() === '') {
            alert('비밀번호를 입력해 주세요');
            return false;
        }

        // 비밀번호 일치여부
        if ($('#pwd').val() !== $('#pwd2').val()) {
            alert('비밀번호가 일치하지 않습니다');
            return false;
        }
    }

    // 이름 입력 안함
    if ($('#name').val() === '') {
        alert('이름을 입력해 주세요');
        return false;
    }

    // 지부 선택 안함
    if ($('#area_idx').val() === '') {
        alert('지부를 선택해 주세요');
        return false;
    }

    // 성별 선택 안함
    if ($('input[name=sex]:checked').val() === undefined) {
        alert('성별을 선택해 주세요');
        return false;
    }

    // 생년월일
    if ($('#birthyr').val() === '' || $('#birthm').val() === '' || $('#birthd').val() === '') {
        alert('생년월일을 올바르게 선택해 주세요');
        return false;
    }

    // 연락처
    if (!contact_regex.test(contact)) {
        alert('올바른 연락처 정보를 입력해 주세요');
        return false;
    }

    // 소속교회
    if ($('#church').val() === '') {
        alert('소속 교회를 입력해 주세요');
        return false;
    }

    // 참가 구분
    if ($('input[name=persontype]:checked').val() === undefined) {
        alert('참가구분을 선택해 주세요');
        return false;
    }

    // 단체버스
    if ($('input[name=bus_yn]:checked').val() === undefined) {
        alert('단체버스 이용 여부를 선택해 주세요');
        return false;
    }

    // MIT 참가 여부
    if ($('input[name=mit_yn]:checked').val() === undefined) {
        alert('MIT참가 여부를 선택해 주세요');
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


    $('#birth').val($('#birthyr').val() + '-' + $('#birthm').val() + '-' + $('#birthd').val());
    $('#contact').val(contact);
    return true;
}

function submit_form() {
    'use strict';
    if (validate_form()) {
        $('#form').submit();
    }
}
