$(document).ready(function(){
    var getIndex = function(selector){
            var index = 0,
                targets = $(selector);

            $.each(targets, function(i){
                index += (targets.eq(i).hasClass('active')) ? i : 0;
            });

            return index;
        },
        playUpInterval = null,
        autoPlayUp = function(){
            if(playUpInterval){
                window.clearInterval(playUpInterval);
            }
            playUpInterval = window.setInterval(function(){
                var targets = $('.slide-nav'),
                    current = getIndex(targets),
                    next = current + 1,
                    next = (next < targets.length) ? next : 0;

                targets.eq(next).click();
            }, 4000);

            // autoPlayLeft();
        },
        playLeftInterval = null,
        autoPlayLeft = function(){
            if(playLeftInterval){
                window.clearInterval(playLeftInterval);
            }
            playLeftInterval = window.setInterval(function(){
                var targets = $('.slide'),
                    current = getIndex(targets);
                    
                targets.eq(current).find('.left-nav').click();
            }, 4000);
        };

    // 上下切换
    $('.slide-nav').on('click', function(){

        $('.slide-nav').removeClass('active');
        $(this).addClass('active');

        $('.slide').removeClass('active');
        $('.slide').eq(getIndex('.slide-nav')).addClass('active');

        autoPlayUp();
    });

    // 左右切换
    $('.left-nav').on('click', function(){
        
        var targets = $(this).parent().find('.slide-img'),
            index = getIndex(targets),
            length = targets.length;
        
        index -= 1;
        index = (index == -1) ? (length-1) : index;
        
        targets.removeClass('active');
        targets.eq(index).addClass('active');

        autoPlayUp();
    });
    $('.right-nav').on('click', function(){
        
        var targets = $(this).parent().find('.slide-img'),
            index = getIndex(targets),
            length = targets.length;
        
        index += 1;
        index = (index == length) ? 0 : index;
        
        targets.removeClass('active');
        targets.eq(index).addClass('active');

        autoPlayUp();
    });

    // 自动播放
    autoPlayUp();
    
    // 数字效果
    new countUp("company-count", 0, $('#company-count').data('count')).start();
    new countUp("person-time-count", 0, $('#person-time-count').data('count')).start();
});