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

                }, i*6000);
                
            });
        };

    window.setInterval(function(){
        loopFadeText();
    }, WORDS.length * 6000);
    
    loopFadeText();
});