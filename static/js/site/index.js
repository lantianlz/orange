$(document).ready(function(){
    var targets = $('.slide-img'),
        isTrans = false,
        transInterval = null,
        autoTrans = function(){
            if(transInterval){
                window.clearInterval(transInterval);
            }
            transInterval = window.setInterval(function(){
                var current = getIndex(),
                    next = current + 1,
                    next = (next < targets.length) ? next : 0;

                trans(next);
                
            }, 11000);
        },
        getIndex = function(){
            var index = 0;

            $.each(targets, function(i){
                index += (targets.eq(i).hasClass('slide-in')) ? i : 0;
            });

            return index;
        },
        // 调用文字插件方法
        _textillate = function(selector){
            var target = $(selector);

            target.children.length > 0 ? target.textillate('start') : target.textillate();
        },
        _resetText = function(index){
            var target = '.banner-box-' + index;
            $(target + ' .eng-text>span>span').hide();
            $(target + ' .text-1').css('opacity', '0').removeClass('fadeInUp');
            $(target + ' .text-2').css('opacity', '0').removeClass('fadeInDown');
            $(target + ' .text-3>span>span').hide();
            $(target + ' .text-4>span>span').hide();
            $(target + ' .text-5>span>span').hide();
            $(target + ' .tag').hide();
        }
        // 文字效果
        _textTrans = function(next){
            var nextNode = '.banner-box-' + (next + 1);
            
            // 设置效果
            $(nextNode + ' .text-1').css('opacity', '1').addClass('fadeInUp');
            $(nextNode + ' .text-2').css('opacity', '1').addClass('fadeInDown');
            window.setTimeout(function(){
                _textillate(nextNode + ' .eng-text');
            }, 800);
            window.setTimeout(function(){
                _textillate(nextNode + ' .text-3');
                _textillate(nextNode + ' .text-4');
            }, 1800);
            window.setTimeout(function(){
                _textillate(nextNode + ' .text-5');
            }, 2800);
            window.setTimeout(function(){
                $(nextNode + ' .tag').show().removeClass("bounceIn").addClass("bounceIn");
                isTrans = false;
            }, 3800);
        },
        trans = function(next){
            var current = getIndex();
            _resetText(next+1);

            // current 面板收线  0.5s
            $('.banner-box').eq(current).removeClass('active');
            //  current 文字框隐藏  0.3s
            window.setTimeout(function(){
                $('.banner-box').eq(current).css('opacity', 0);
            }, 600);
            // current 面板隐藏  0.5s
            window.setTimeout(function(){
                targets.eq(current).removeClass("slide-in").addClass("slide-out");
            }, 900);
            // next 面板显示  0.5s
            window.setTimeout(function(){
                targets.eq(next).removeClass("slide-out").addClass("slide-in");
            }, 1400);
            // next 面板显示 0.3s
            window.setTimeout(function(){
                $('.banner-box').eq(next).css('opacity', 1);
            }, 1900);
            // next 面板文字框 0.5s
            window.setTimeout(function(){
                $('.banner-box').eq(next).addClass('active');
            }, 2200);
            // 文字效果  4s
            window.setTimeout(function(){
                _textTrans(next);
            }, 2600);

            // 导航
            $('.slide-nav-item').removeClass("active");
            $('.slide-nav-item').eq(next).addClass("active");
        };
    
    // 导航的点击事件
    $('.slide-nav-item').on("click", function(){
        // 动画是否正在进行
        if(isTrans == true){
            return;
        } else {
            isTrans = true;
        }

        var index = $(this).data('index');
        trans(index);
        autoTrans();
    });

    // 自动轮播
    autoTrans();

    // 第一次效果
    window.setTimeout(function(){
        
        $('.banner-box').eq(3).css('opacity', 1);
        window.setTimeout(function(){
            $('.banner-box').eq(3).addClass('active');
        }, 300);
        window.setTimeout(function(){
            _textTrans(3);
        }, 800);

    }, 300);
    
});