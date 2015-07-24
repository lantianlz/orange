$(document).ready(function(){
    /*
        城市切换效果
    */
    var CITY_COOR = {
            0: {'left': 430, 'top': 270},
            1: {'left': 600, 'top': 110},
            2: {'left': 670, 'top': 270}
        },
        isTrans = false;

    $('.city').on('click', function(){
        // 动画是否正在进行
        if(isTrans == true){
            return;
        } else {
            isTrans = true;
        }

        $('.city').removeClass('active');
        $(this).addClass('active');

        var city = $(this).data('city'),
            coor = CITY_COOR[city];

        $('.contact-card').hide('fast');
        $('.location-wave').fadeOut('fast');
        window.setTimeout(function(){
            $('.location').removeClass('location-wave-in').addClass('location-wave-out');
        }, 300);
        window.setTimeout(function(){
            $('.location')
            .css({
                'left': coor.left,
                'top': coor.top
            })
            .removeClass('location-wave-out')
            .addClass('location-wave-in');
        }, 1400)

        window.setTimeout(function(){
            $('.contact-card')
            .css({
                'left': coor.left + 100,
                'top': coor.top - 20
            })
            .show('fast', function(){
                $(this).css('overflow', 'inherit')
            });
            $('.location-wave').fadeIn('fast');
            isTrans = false;
        }, 2400);
    });
});