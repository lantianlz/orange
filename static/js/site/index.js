$(document).ready(function(){
    var targets = $('.slide-img'),
        getIndex = function(){
            var index = 0;

            $.each(targets, function(i){
                index += (targets.eq(i).hasClass('slide-in')) ? i : 0;
            });

            return index;
        },
        trans = function(next){
            var current = getIndex();
            
            targets.eq(current).removeClass("slide-in").addClass("slide-out");
            window.setTimeout(function(){
                targets.eq(next).removeClass("slide-out").addClass("slide-in");
            }, 500);

            $('.slide-nav-item').removeClass("active");
            $('.slide-nav-item').eq(next).addClass("active");
        };
    
    $('.slide-nav-item').on("click", function(){
        var index = $(this).data('index');
        trans(index);
    });

    window.setInterval(function(){
        var current = getIndex(),
            next = current + 1,
            next = (next < targets.length) ? next : 0;

        trans(next);
        
    }, 5000)
});