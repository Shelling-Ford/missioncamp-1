/*global $, document, alert, validator */

function checkPersontype() {
  if ($('input[name=persontype]:checked').val() === '중학생' || $('input[name=persontype]:checked').val() === '고등학생') {
    $('.school').show();
  } else {
    $('.school').hide();
  }
}


$(document).ready(function () {
  'use strict';
  $('#userid').change(check_userid);
  $('#pwd2').change(check_pwd);

  checkPersontype();
  $('input[name=persontype]').change(checkPersontype);

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
  var userid = $('#userid').val(), email_regex = /^[a-z]?[a-z0-9\-\_]{4,}$/i;

  if (!email_regex.test(userid)) {
    $('#id_check').html('아이디는 영문 소문자 및 숫자 4글자 이상 입력해주세요');
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

function check_pwd() {
  if ($('#pwd').val() !== $('#pwd2').val()) {
    $('#pwd_check').html("비밀번호가 일치하지 않습니다.")
    $('#pwd_check').removeClass('text-success').addClass('text-danger');
  } else {
    $('#pwd_check').html("")
  }
}

// 폼 검증 함수
function validate_form() {
    'use strict';
    var contact_regex = /^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$/, contact = $('#hp').val() + '-' + $('#hp2').val() + '-' + $('#hp3').val();
    var group_idx = $('input[name=group_idx]').val()

    // 이메일 중복검사
    if (!isChecked && typeof(group_idx) == "undefined" ) {
        alert('아이디와 비밀번호를 입력해주세요');
        return false;
    }

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

    //  개인 신청일 경우
    // 신청자가 중고등학생 일 경우 학교를 입력하게 함.
    if (($('input[name=persontype]:checked').val() === '중학생' || $('input[name=persontype]:checked').val() === '고등학생') && typeof(group_idx) == "undefined") {
	    if ($('#sch1').val() === '') {
	    	alert('학교를 입력해주세요');
	    	return false;
	    }
    }

    // 단체버스
    if ($('input[name=bus_yn]:checked').val() === undefined) {
        alert('단체버스 이용 여부를 선택해 주세요');
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
