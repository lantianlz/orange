/*
    为字符串拓展format方法
    用例：
    String.format('{0}, {1}!', 'Hello', 'world');
*/
if (!String.format) {
    String.format = function(src){
        if (arguments.length == 0){
            return null;
        }

        var args = Array.prototype.slice.call(arguments, 1);
        return src.replace(/\{(\d+)\}/g, function(m, i){
            return args[i];
        });
    };
}


(function($){

    /*
        给指定元素生成一个唯一id, 主要使用场景ajax需要一个id，防止多次点击

        用例：
        $('.someclass').setUUID();
    */
    $.fn.setUUID = function(){
        return this.each(function(){
            return $(this).attr('id', new Date().getTime());
        });
    }

    $.Global = {}

    /* 
        网站提示插件
    */
    $.Global.Notice = {
        version: '1.0.0',
        author: 'stranger',
        description: '网站提示插件'
    };
    /*
        顶部通知
        content: 通知内容
        type: 是否重要通知

        用例:
        $.Global.Notice.TopNotice('info', '这是通知', 2000);
    */
    $.Global.Notice.TopNotice = function(type, content, closeSeconds){
        var noticeHtml = [
                '<div class="alert alert-dismissable pf box-shadow-224 border-radius-2 co-ffffff zx-top-notice orange-{0}-notice">',
                    '<button type="button" class="close" aria-hidden="true">',
                        '<span class="fa fa-times co5 f18 pointer"></span>',
                    '</button>',
                    '<span class="fa {1} pa pr-10 f20" style="left: 25px; top: 15px;"></span>',
                    '<span class="notice-content pl-50">{2}</span>',
                '</div>'
            ].join(''),
            // 图标
            signDict = {
                'success': 'fa-check', 
                'error': 'fa-minus-circle',
                'warning': 'fa-warning',
                'info': 'fa-info-circle'
            },
            sign = signDict[type ? type : 'info'];


        var target = $(String.format(noticeHtml, type, sign, content)).appendTo($('body')),
            left = ($(window).width() - target.width()) / 2 - 30;

        target
        .css({'left': left > 0 ? left : 0 , 'top': -55})
        .animate({'top': 7}, 300);

        target
        .find('.close')
        .bind('click', function(){
            // 关闭之后删除自己
            target.animate({'top': -55}, 300, function(){target.remove()});
        });

        // 自动关闭时间
        if(closeSeconds){
            window.setTimeout(function(){
                target.animate({'top': -55}, 300, function(){target.remove()});
            }, closeSeconds);
        }

    };

    // 成功信息
    $.Global.Notice.SuccessTopNotice = function(content){
        $.Global.Notice.TopNotice('success', content, 3000);
    };

    // 错误信息
    $.Global.Notice.ErrorTopNotice = function(content){
        $.Global.Notice.TopNotice('error', content);
    };

    // 普通信息
    $.Global.Notice.InfoTopNotice = function(content){
        $.Global.Notice.TopNotice('info', content, 3000);
    };

    // 警告信息
    $.Global.Notice.WarningTopNotice = function(content){
        $.Global.Notice.TopNotice('warning', content);
    };
    

})(jQuery);

/*
    jQuery.validate 中文提示
*/
if(jQuery.validator){
    jQuery.extend(jQuery.validator.messages, {
        required: "必填字段",
        remote: "请修正该字段",
        email: "请输入正确格式的电子邮件",
        url: "请输入合法的网址",
        date: "请输入合法的日期",
        dateISO: "请输入合法的日期 (ISO).",
        number: "请输入合法的数字",
        digits: "只能输入整数",
        creditcard: "请输入合法的信用卡号",
        equalTo: "请再次输入相同的值",
        accept: "请输入拥有合法后缀名的字符串",
        maxlength: jQuery.validator.format("请输入一个 长度最多是 {0} 的字符串"),
        minlength: jQuery.validator.format("请输入一个 长度最少是 {0} 的字符串"),
        rangelength: jQuery.validator.format("请输入 一个长度介于 {0} 和 {1} 之间的字符串"),
        range: jQuery.validator.format("请输入一个介于 {0} 和 {1} 之间的值"),
        max: jQuery.validator.format("请输入一个最大为{0} 的值"),
        min: jQuery.validator.format("请输入一个最小为{0} 的值")
    });
}


$(document).ready(function(){

    // 给不支持placeholder的浏览器添加此属性
    $('input, textarea').placeholder();

    // 提示信息框
    try {
        if(ERROR_MSG){
            $.Global.Notice.ErrorTopNotice(ERROR_MSG);
        }
        if(SUCCESS_MSG){
            $.Global.Notice.SuccessTopNotice(SUCCESS_MSG);
        }
        if(INFO_MSG){
            $.Global.Notice.InfoTopNotice(INFO_MSG);
        }
        if(WARNING_MSG){
            $.Global.Notice.WarningTopNotice(WARNING_MSG);
        }
    }
    catch(e) {
        alert(e);
    }

    // 点击按钮效果
    $('.btn-wave').on('mousedown', function(e){
        var e = e || window.event,
            offset = $(this).offset(),
            left = e.pageX - offset.left - 20,
            top = e.pageY - offset.top - 20,
            target = $('<span class="wave" style="left: '+left+'px; top: '+top+'px"></span>').appendTo($(this));
        
        target.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function(){
            $(this).remove();
        });
    });

});