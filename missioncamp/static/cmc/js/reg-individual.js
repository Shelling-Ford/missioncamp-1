/* global $, document, alert */
$(document).ready(function () {
    'use strict';
    $('#campus_group').hide();
    $('#major_group').hide();
    $('#job_group').hide();
    $('#date_of_arrival_group').hide();
    $('#date_of_leave_group').hide();

    // 참가구분 == 청년 일때 직업란 보여줌
    // 그 외는 모두 숨김
    $('input[name=persontype]').change(function () {
        if ($(this).val() === '청년') {
            $('#campus_group').hide();
            $('#major_group').hide();
            $('#job_group').show();
        } else if ($(this).val() === '대학생') {
            $('#campus_group').show();
            $('#major_group').show();
            $('#job_group').hide();
        } else {
            $('#campus_group').hide();
            $('#major_group').hide();
            $('#job_group').hide();
        }
    });

    // 참가형태 == 부분참가 일때 참가기간 선택 보여줌
    // 그 외는 모두 숨김
    $('input[name=fullcamp_yn]').change(function () {
        if ($(this).val() === '0') {
            $('#date_of_arrival_group').show();
            $('#date_of_leave_group').show();
        } else {
            $('#date_of_arrival_group').hide();
            $('#date_of_leave_group').hide();
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

    $('select[name=foreigner]').change(function () {
      if ($('select[name=foreigner] option:selected').val() === '내국인') {
        $('#nationality').hide();
        $('#nationality').val('');
      } else {
        $('#nationality').show();
      }
    });

    $('#form1').on('submit', validate_form);
    $('#userid').change(check_userid);
});
var isChecked = false;

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function check_userid() {
    'use strict';
    var userid = $('#userid').val(), campidx = $('#campidx').val(), email_regex = /^[a-z]?[a-z0-9\-\_]{4,}$/i;

    if (!validateEmail(userid)) {
        $('#id_check').html('올바른 이메일을 입력해주시기 바랍니다.');
        $('#id_check').removeClass('text-success').addClass('text-danger');
        isChecked = false;
        return;
    }

    $.ajax({
        url: './check-userid',
        type: 'POST',
        data: 'userid=' + userid,
        success: function (data) {
            if (parseInt(data, 10) === 0) {
                $('#id_check').html("사용이 가능한 아이디입니다.")
                $('#id_check').removeClass('text-danger').addClass('text-success');
                isChecked = true;
            } else {
                $('#id_check').html("사용이 불가한 아이디입니다.")
                $('#id_check').removeClass('text-success').addClass('text-danger');
                isChecked = false;
            }
        }
    });
}



// 폼 검증 함수
function validate_form() {

    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, contact = $('#hp').val() + '-' + $('#hp2').val() + '-' + $('#hp3').val();
    var group_idx = $('input[name=group_idx]').val()

    // 이메일 중복검사
    if (!isChecked && $('#userid').length) {
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
    if ($('#area_idx').val() === '' && $('#area_idx').length) {
        alert('지부를 선택해 주세요');
        return false;
    }

    // 성별 선택 안함
    if ($('input[name=sex]:checked').val() === undefined) {
        alert('성별을 선택해 주세요');
        return false;
    }

    // 생년월일
    if ($('#birth').val() === '') {
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
        alert('2017 겨울 FO/MIT참가 여부를 선택해 주세요');
        return false;
    }

    // 비전스쿨 수료 여부
    if ($('input[name=vision_yn]:checked').val() === undefined) {
        alert('비전스쿨 수료 여부를 선택해 주세요');
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


    // $('#birth').val($('#birthyr').val() + '-' + $('#birthm').val() + '-' + $('#birthd').val());
    $('#contact').val(contact);
    return true;
}
