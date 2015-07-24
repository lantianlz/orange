$(document).ready(function(){
    // 文字效果切换
    var WORDS = [
            ['是中国最好的', '服务实体连锁店', '让你体验不一样', '实体店'],
            ['是中国最好的', '服务平台', '为你提供最好', '汽车后服务']
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

                }, i*4000);
                
            });
        };

    window.setInterval(function(){
        loopFadeText();
    }, WORDS.length * 4000);
    
    loopFadeText();
});