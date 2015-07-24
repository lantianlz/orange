$(document).ready(function(){

    $('#fullpage').fullpage({
        scrollingSpeed: 700,
        easing: 'easeOutExpo',
        navigation: true,
        onLeave: function(index, nextIndex, direction){

            // pageTransform(nextIndex);
            
        }
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
        window.setTimeout(function(){
            $('.btn-booking-1').addClass('tada');
        }, 100);
    }, 8000);

});