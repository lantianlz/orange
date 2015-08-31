$(document).ready(function(){

    $('#fullpage').fullpage({
        scrollingSpeed: 700,
        easing: 'easeOutExpo',
        navigation: true,
        lockAnchors: false
    });


    /*
        第一屏效果
    */
    var TEXT_1 = "新鲜多一点".split(""),
        TEXT_2 = "乐趣多一点".split(""),
        rotate1 = function(){
            var targets = $(".rotate-text-1 span");
            $.each(targets, function(i){
                window.setTimeout(function(){
                    targets.eq(i).addClass('rotate-y');
                }, 100*i);
            });
        },
        rotate2 = function(){
            var targets = $(".rotate-text-2 span");
            $.each(targets, function(i){
                window.setTimeout(function(){
                    targets.eq(i).addClass('rotate-x');
                }, 100*i);
            });
        };
    $.map(TEXT_1, function(i){
        $('.rotate-text-1').append('<span class="rotate-text">'+i+'</span>');
    });
    $.map(TEXT_2, function(i){
        $('.rotate-text-2').append('<span class="rotate-text">'+i+'</span>');
    });
    window.setTimeout(rotate1, 400);
    window.setTimeout(rotate2, 1800);

    // 预订效果
    window.setInterval(function(){
        $('.btn-booking-1').removeClass('tada');
        $('.btn-booking-4').removeClass('tada');
        window.setTimeout(function(){
            $('.btn-booking-1').addClass('tada');
            $('.btn-booking-4').addClass('tada');
        }, 100);
    }, 8000);

    // 点击预订跳转
    var goBooking = function(e){
        e.preventDefault();
        $.fn.fullpage.moveTo(6);
        window.setTimeout(function(){
            $('.name').focus();
        }, 300);
    }
    $('.btn-booking-1').on('mousedown', goBooking);
    $('.btn-booking-3').on('mousedown', goBooking);
    $('.btn-booking-4').on('mousedown', goBooking);

    var is_ajaxing = false;
    // 预约
    $('.btn-booking-2').on('mousedown', function(){
        
        var name = $('.name').val(),
            company = $('.company').val(),
            mobile = $('.mobile').val();

        if($.trim(name) == "" || $.trim(company) == "" || $.trim(mobile) == ""){
            $.Global.Notice.InfoTopNotice("请输入完整的信息");
            return;
        }

        if(is_ajaxing){
            return;
        }
        is_ajaxing = true;

        ajaxSend(
            "/company/get_booking",
            {'name': name, 'company': company, 'mobile': mobile, 'source': 0}, 
            function(data){
                if(data.errcode == "0"){
                    $.Global.Notice.SuccessTopNotice('预约成功，稍后市场专员将与您联系');
                } else {
                    $.Global.Notice.InfoTopNotice(data.errmsg);
                }
                is_ajaxing = false;
            }
        )
    });
});