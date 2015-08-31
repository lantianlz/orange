$(document).ready(function(){
    var isTrans = false,
    	transform = function(index){
        var OUT_EFFECTS = {
                0: 'move-up-out',
                1: 'move-down-out',
                2: 'slide-up-out',
                3: 'slide-down-out',
                4: 'slide-left-out',
                5: 'slide-right-out'
            },
            IN_EFFECTS = {
                0: 'move-up-in',
                1: 'move-down-in',
                2: 'slide-up-in',
                3: 'slide-down-in',
                4: 'slide-left-in',
                5: 'slide-right-in'
            },
            getOutEffect = function(){
                return OUT_EFFECTS[Math.round(Math.random() * 5)];
            },
            getInEffect = function(){
                return IN_EFFECTS[Math.round(Math.random() * 5)];
            },
            outEffect = getOutEffect(),
            inEffect = getInEffect(),
            prev = $('.slides>li.active'),
            next = $('.slides>li').eq(index);

        // outEffect = "slide-down-out";
        // inEffect = "slide-right-in";

        // 纠正下效果
        // if([1, 3, 5].indexOf(index) > -1){
        //     outEffect = (outEffect == "slide-down-out") ? "slide-up-out" : outEffect;
        //     outEffect = (outEffect == "slide-right-out") ? "slide-left-out" : outEffect;
        //     inEffect = (inEffect == "slide-right-in") ? "slide-left-in" : inEffect;
        //     inEffect = (inEffect == "slide-down-in") ? "slide-up-in" : inEffect;
        // }

        prev.removeClass('active');
        prev.addClass('s-hide');
        prev.find('img').eq(0).addClass(outEffect);
        window.setTimeout(function(){
            prev.find('img').eq(1).addClass(outEffect);
        }, 250);
        window.setTimeout(function(){
            prev.removeClass('s-hide');
            prev.find('img').eq(0).removeClass(outEffect);
            prev.find('img').eq(1).removeClass(outEffect);
        }, 1750);

        next.addClass('active s-show');
        window.setTimeout(function(){
            next.find('img').eq(0).addClass(inEffect);
        }, 800);
        window.setTimeout(function(){
            next.removeClass('s-show');
            next.find('img').eq(1).addClass(inEffect);
        }, 1050);
        window.setTimeout(function(){
            next.find('img').eq(0).removeClass(inEffect);
            next.find('img').eq(1).removeClass(inEffect);

            isTrans = false;
        }, 2550);
    };

    // 导航事件
    $('.slide-nav-item').on('click', function(){
    	// 动画是否正在进行
        if(isTrans == true){
            return;
        } else {
            isTrans = true;
        }

        var target = $(this);

        if(target.hasClass('active')){
            return;
        }

        $('.slide-nav-item.active').removeClass('active');
        target.addClass('active');
        transform(parseInt(target.data('index')));
    });

    // 自动跳转
    window.setInterval(function(){
        var currentIndex = $('.slide-nav-item.active').data('index') + 1;
        
        currentIndex = (currentIndex >= $('.slide-nav-item').length) ? 0 : currentIndex;
        
        $('.slide-nav-item').eq(currentIndex).click();
    }, 7000);

    window.setTimeout(function(){
        $('.slide-nav-item').eq(1).click();
    }, 2000);


    var showScaleModal = function(){
        var HTML = [
            '<div class="modal fade" id="win-modal">',
              '<div class="modal-dialog">',
                '<div class="modal-content">',
                  '<div class="modal-header">',
                    '<button type="button" class="close hide" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>',
                    '<h4 class="modal-title text-center letter-spacing-3">咕咚网</h4>',
                  '</div>',
                  '<div class="modal-body">',
                    '<img class="w" src="'+MEDIA_URL+'img/customers/1.jpg" />',
                  '</div>',
                  '<div class="modal-footer">',
                    '<a class="btn btn-default btn-modal" data-dismiss="modal">CLOSE ME</a>',
                  '</div>',
                '</div>',
              '</div>',
            '</div>'
        ];

        $('#win-modal').remove();

        $('body').append(HTML.join(""));

        $('#win-modal').modal('show');
    };

    $('.customer-img').on("click", function(){
    	showScaleModal();
    });


    // 数字效果
    new countUp("company-count", 0, $('#company-count').data('count')).start();
    new countUp("person-time-count", 0, $('#person-time-count').data('count')).start();
});