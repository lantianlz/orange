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

	$.Global.Utils = {
        version: '1.0.0',
        author: 'stranger',
        description: '工具包'
    };

    /*
        字典映射

        用例：
        $.Global.Utils.dictMap({'a': '1', 'b': '2'}, {'a': 'a1', 'b': 'b1'})
        返回 {'a1': '1', 'b1': '2'}
    */
    $.Global.Utils.dictMap = function(originDict, maps){
        var newDict = {};
        
        if(!originDict){
            return null;
        }
        
        for(var m in maps){
            newDict[m] = originDict[maps[m]]
        }

        return newDict;
    };

    /*
        批量字典映射解析

        $.Global.Utils.dictMapParse([{'a': '1', 'b': '2'}], {'a': 'a1', 'b': 'b1'});
    */
    $.Global.Utils.dictMapParse = function(data, maps){
        var temp = [];

            _.each(data, function(d){
                temp.push($.Global.Utils.dictMap(d, maps));
            });

        return temp;
    };

    /*
        自动补零
        始终返回两位字符串，不够自动补零

        用例:
        $.Global.Utils.addZero('0');
    */
    $.Global.Utils.addZero = function(data){
        var temp = data + '';
        if(temp.length === 0){
            return '00'
        } else if(temp.length === 1){
            return  '0' + temp;
        } else{
            return data;
        }
    };

    /*
        格式化日期
        返回字符串  可带格式 y-m-d、h:m:s、y-m-d h:m:s

        用例:
        $.Global.Utils.formatDate(new Date());
        $.Global.Utils.formatDate(new Date(), 'y-m-d');
    */
    $.Global.Utils.formatDate = function(date, format){

        var str = "",
            year = $.Global.Utils.addZero(date.getFullYear()),
            month = $.Global.Utils.addZero(date.getMonth()+1), 
            day = $.Global.Utils.addZero(date.getDate()),
            hours = $.Global.Utils.addZero(date.getHours()),
            minutes = $.Global.Utils.addZero(date.getMinutes()),
            seconds = $.Global.Utils.addZero(date.getSeconds());

        switch(format){
            case 'y-m-d': 
                str = String.format('{0}-{1}-{2}', year, month, day);
                break;
            case 'h:m:s':
                str = String.format('{0}:{1}:{2}', hours. minutes, seconds);
                break;
            default:
                str = String.format('{0}-{1}-{2} {3}:{4}:{5}', year, month, day, hours, minutes, seconds);
                break;
        }
        return str;

    };

    /*
        将表单数据转换成字典，用于ajax

        用例:
        $.Global.Utils.formToDict('myform');
    */
    $.Global.Utils.formToDict = function(selector){
        var postData = {};

        // 转换
        _.map($(selector).serializeArray(), function(i){
            // 是否有值
            if(i.value){
                
                // 是否已经存在此name的值，主要用于name相同的控件
                if(!$.isEmptyObject(postData[i.name])){
                    
                    // 是否第一次添加
                    if(!(postData[i.name] instanceof Array)){
                        postData[i.name] = [postData[i.name]];
                    }
                        
                    postData[i.name].push(i.value);
                    
                } else {
                    postData[i.name] = i.value;
                }
            }
        });

        return postData;
    };

    /*
        格式化价钱

        用例:
        $.Global.Utils.formatPrice(12.5);
    */
    $.Global.Utils.formatPrice = function(price){
        var price = Math.round(parseFloat(price) * 100) / 100;

        price = price + '';

        if(price.indexOf('.') > -1){
            if(price.split('.')[1].length == 1){
                return price + '0';
            } else {
                return price;
            }
        } else {
            return price + '.00';
        }
    };

    /*
        获取url参数

        用例:
        $.Global.Utils.getQueryString('name');
    */
    $.Global.Utils.getQueryString = function(name){
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i"),
            r = window.location.search.substr(1).match(reg);
        
        if(r != null){
            return decodeURI(r[2]);
        }

        return null;
    }

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
                '<div class="alert alert-dismissable pf box-shadow-224 border-radius-2 co5 zx-top-notice qx-{0}-notice">',
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
        .css({'left': left > 0 ? left : 0 , 'top': 0})
        .animate({'top': 55}, 300);

        target
        .find('.close')
        .bind('click', function(){
            // 关闭之后删除自己
            target.animate({'top': 0}, 300, function(){target.remove()});
        });

        // 自动关闭时间
        if(closeSeconds){
            window.setTimeout(function(){
                target.animate({'top': 0}, 300, function(){target.remove()});
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


    /*
        分页组件
    */
    $.Global.Pagination = {
        version: '1.0.0',
        author: 'stranger',
        description: '分页组件'
    }
    /*
        分页组件
    */
    $.Global.Pagination.PaginationView = Backbone.View.extend({
        el: '.qx-pagination',

        step: 4,

        totalStep: 10,

        searchUrl: 'search',

        // 防止超出范围
        _protectRange: function(tempMin, tempMax, min, max){
            if(tempMin < min){
                tempMin = min;
            }

            if(tempMax > max){
                tempMax = max
            }

            return [tempMin, tempMax]
        },

        // 生成分页区间
        _generateRange: function(current, total){
            var pages = [], 
                current = parseInt(current),
                total = parseInt(total),
                min = current - this.step,
                max = current + this.step,
                temp = [];

            // 防止超出范围
            temp = this._protectRange(min, max, 1, total);
            min = temp[0];
            max = temp[1];

            // 维持列表在 totalStep-1 这个长度
            var tempCount = max - min + 2;
            if(tempCount < this.totalStep){
                if(max >= total){
                    max = total;
                    min = max - this.totalStep + 2;
                } else {
                    max = this.totalStep - 1;
                }
            }

            // 防止超出范围
            temp = this._protectRange(min, max, 1, total);

            // 生成列表
            pages = _.range(temp[0], temp[1]+1);

            return pages;
        },

        render: function(pageIndex, pageCount, searchUrl){
            var url = searchUrl || this.searchUrl,
                pageHtml = '',
                pages = this._generateRange(pageIndex, pageCount);
            
            for (var i = 0; i < pages.length; i++) {

                pageHtml += String.format(
                    '<li {0}><a href="#{1}/{2}">{3}</a></li>', 
                    pages[i] == pageIndex ? 'class="active"' : '', // 为当前页添加active类
                    url, 
                    pages[i], 
                    pages[i]
                );
            };

            // 首页
            pageHtml = String.format(
                '<li {0}><a href="{1}">&laquo;</a>', 
                pageIndex == 1 ? 'class="disabled"' : '',
                pageIndex == 1 ? 'javascript: void(0);' : ('#' + url + '/' + 1)
            ) + pageHtml;
            
            // 末页
            pageHtml += String.format(
                '<li {0}><a href="{1}">&raquo;</a>', 
                pageIndex == pageCount ? 'class="disabled"' : '',
                pageIndex == pageCount ? 'javascript: void(0);' : ('#' + url + '/' + pageCount)
            );

            this.$el.html(pageHtml);
        }
    });


    /*
        文本框组件
    */
    $.Global.TextboxList = {
        version: '1.0.0',
        author: 'stranger',
        description: '文本框组件'
    };
    /**/
    $.Global.TextboxList.create = function(selector, options){
        var temp = new $.TextboxList(selector, {
            bitsOptions: {
                box: {deleteButton: true}
            },
            unique: true, 
            max: options.max,
            plugins: {
                autocomplete: {
                    minLength: 2, // 最小字符
                    queryRemote: true, // 远程查询
                    placeholder: options.placeholder,
                    highlight: false,
                    onlyFromValues: true, // 是否默认选中第一个结果
                    remote: {
                        url: options.url, 
                        param: options.param,
                        loadPlaceholder: options.loadPlaceholder,
                    }
                }
            }

        });

        return {
            target: temp,
            add: function(name, value){
                temp.add(name, value)
            },
            getValues: function(){
                return _.map(temp.getValues(), function(v){return v[0]});
            }
        };
    };


    $.Global.Animation = {
        version: '1.0.0',
        author: 'stranger',
        description: '动画组件'
    };

    /*
    sprite图片的动画插件

    selector: 选择器
    options.imgSrc: 图片的路径(将所有桢竖着依次排列)
    options.height: 每一帧的高度,
    options.fps: fps,
    options.loop: 是否循环播放

    原理: 将动画分解成多桢，然后每隔一小段时间去换桢

    用例: 
    $.Global.Animation.SpriteAnimation(
        '.sprite-car', {
            imgSrc: '{{MEDIA_URL}}img/sprite-plane.png', 
            height: 89
        }
    );
    */
    $.Global.Animation.SpriteAnimation = function(selector, options){
        var defaults = {
                imgSrc: null,
                height: null,
                fps: 24,
                loop: true
            },
            opts = $.extend(defaults, options),
            target = $(selector);
            
        if(opts.imgSrc == null || opts.height == null){
            console.log('没有指定可用的参数，imgSrc 或 height 为空。');
            return;
        }

        var img = new Image();
        img.style.display = "none";
        img.onload = function(){

            var count = 0,
                spriteInterval = null,
                total = Math.floor(img.height / opts.height),
                total = (img.height % opts.height == 0) ? total : (total + 1);

            // 设置元素属性
            target
            .css({
                'width': img.width,
                'height': opts.height,
                'position': 'relative',
                'overflow': 'hidden'
            })
            .append('<img style="top: 0; position: absolute;" src="' + opts.imgSrc + '">');

            // 设置动画
            spriteInterval = window.setInterval(function(){
                count += 1;

                if(count >= total){
                    // 是否循环播放
                    if(opts.loop){
                        count = 0;
                    } else {
                        window.clearInterval(spriteInterval);
                    }
                }

                target.children().css({'top': -opts.height * count});

            }, 1000 / opts.fps);
        };

        $('body').append(img);
        img.src = opts.imgSrc;

    }

})(jQuery);


/*
    创建 KindEditor 编辑器
    selector: textarea的选择器
*/
function createEditor(selector, imgType){
    return KindEditor.create(selector, {
        resizeType : 1,
        width: '100%',
        //autoHeightMode : true,
        allowPreviewEmoticons : true,
        allowImageUpload : true,
        allowImageRemote: true,
        // basePath: '/',
        uploadJson: MAIN_DOMAIN+'/save_img?img_type='+(imgType||""),
        pasteType : 1,
        cssData: 'body{font-family: "Helvetica Neue",Helvetica,"Lucida Grande","Luxi Sans",Arial,"Hiragino Sans GB",STHeiti,"Microsoft YaHei","Wenquanyi Micro Hei","WenQuanYi Micro Hei Mono","WenQuanYi Zen Hei","WenQuanYi Zen Hei Mono",LiGothicMed; font-size: 14px; color: #222;}',
        themesPath: MEDIA_URL + "css/kindeditor/themes/",
        pluginsPath: MEDIA_URL + "js/kindeditor/plugins/",
        langPath: MEDIA_URL + "js/kindeditor/",
        items : [
            'fontname', 'fontsize', 'forecolor', 'hilitecolor', 'bold', 'italic', 'underline', 'removeformat', '|', 
            'justifyleft', 'justifycenter', 'justifyright', 'insertorderedlist', 'insertunorderedlist', '|', 
            'image', 'multiimage', 'link', '|',
            'fullscreen'
        ],
        afterCreate : function() { 
            //this.loadPlugin('autoheight');
        }, 
        afterBlur:function(){ 
            this.sync(); 
        },
        afterUpload : function(url) {
        }
    });
};

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

    // 统一返回按钮事件处理
    $('.go-back').bind('click', function(){
        if(document.referrer.indexOf('172.16.') > -1 || document.referrer.indexOf('3-10.cc') > -1){
            history.go(-1);
        } else {
            if(typeof(PARENT_URL) != "undefined" && PARENT_URL != ""){
                window.location.href = PARENT_URL;
            } else {
                window.location.href = "/";
            }
        }
        
    });

});