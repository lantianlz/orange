$(document).ready(function(){
    /*
        城市切换效果
    */
    var CITY_COOR = {
            0: {'left': 470, 'top': 470, 'isOpen': true},
            1: {'left': 655, 'top': 290, 'isOpen': false},
            2: {'left': 735, 'top': 455, 'isOpen': false}
        },
        isTrans = false;

    $('.open-already').show();
    $('.open-soon').hide();
    
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
        if(coor.isOpen){
            $('.open-already').show();
            $('.open-soon').hide();
        }
        else{
            $('.open-already').hide();
            $('.open-soon').show();
        }
        window.setTimeout(function(){
            $('.location').removeClass('location-wave-in').addClass('location-wave-out');
        }, 250);
        window.setTimeout(function(){
            $('.location')
            .css({
                'left': coor.left,
                'top': coor.top
            })
            .removeClass('location-wave-out')
            .addClass('location-wave-in');
        }, 900)

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
        }, 1650);
    });
});