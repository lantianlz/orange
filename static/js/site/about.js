$(document).ready(function(){
    // 文字效果切换
    var WORDS = [
            ['是企业', '服务提供商', '为大家提供最优质', '产品', '新鲜的水果'],
            ['是一家专注于', 'O2O的公司', '为广大企业提供最可口', '产品', '可口的点心'],
            ['除去传统的', '供应链的中间环节', '为大家提供性价比更高', '产品', '实惠的产品']
        ],
        getWordWidth = function(word){
            var temp = $('<span style="font-weight: bold; visibility: hidden;">'+word+'</span>').appendTo('.fade-move'),
                width = temp.width();

            temp.remove();
            return width;
        },
        fadeText = function(words){
            $.each(words, function(i){

                $('.fade-text').eq(i)
                .animate({
                    'opacity': 0,
                    'width': getWordWidth(words[i])
                }, 500, 'easeOutExpo', function(){
                    
                    $(this).text(words[i]);
                    $(this).animate({
                        'opacity': 1
                    }, 500, 'easeInExpo');

                });

            });
        },
        loopFadeText = function(){
            $.each(WORDS, function(i){

                window.setTimeout(function(){

                    fadeText(WORDS[i]);

                }, i * 4000);
                
            });
        };

    window.setInterval(function(){
        loopFadeText();
    }, WORDS.length * 4000);
    
    loopFadeText();


    // 员工效果
    $('.employee')
    .on('mousemove', function(e){
        
        var HEIGHT = 262,
            x = e.offsetX,
            width = $(this).width();

        if ( 0 <= x && x <= width/3 ) {
            $(this).css("background-position", "0 -197px");
        } else if ( width/3 <= x && x <= width/3*2 ) {
            $(this).css("background-position", "0 -393px");
        } else if ( width/3*2 <= x && x <= width ) {
            $(this).css("background-position", "0 -589px");
        }
    })
    .on('mouseleave', function(e){
        $(this).css("background-position", "0 0");
    });
});