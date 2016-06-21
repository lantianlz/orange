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
        格式化价格
        price: 要格式化的价格
        num: 保留几位小数

        用例:
        $.Global.Utils.formatPrice(1.23456);
    */
    $.Global.Utils.formatPrice = function(price, num){
        var _num = num || 2;
        return parseFloat(price).toFixed(_num);
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
                    minLength: 1, // 最小字符
                    maxResults: 15,
                    queryRemote: true, // 远程查询
                    placeholder: options.placeholder,
                    searchAll: options.searchAll,
                    highlight: false,
                    onlyFromValues: true, // 是否默认选中第一个结果
                    remote: {
                        url: options.url, 
                        param: options.param,
                        loadPlaceholder: options.loadPlaceholder
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

    /*
        组件view
    */
    $.Global.ComponentView = {
        version: '1.0.0',
        author: 'stranger',
        description: '组件view'
    }
    /*
        产品项目组件
    */
    $.Global.ComponentView.ItemsView = Backbone.View.extend({
        el: '#items-view',
        // 售价  初始化时传入,核算毛利使用
        totalSalePrice: 0,

        _items: [],
        _itemTypes: [],
        _initItemIds: [],

        _modelMaps: {
            'value': 'name',
            'data': 'item_id',
            'price': 'net_weight_price',
            'salePrice': 'sale_price',
            'itemType': 'item_type',
            'spec': 'spec',
            'specText': 'spec_text',
            'des': 'des',
            'smartDes': 'smart_des',
            'amount': 'amount'
        },

        _html: [
            '<ul class="list-unstyled items-view">',
                '<div class="pb-15 border-bottom-1 bdc-e4e4e4 mb-15 pr item-header">',
                    '<input type="text" class="form-control search-item" placeholder="输入茶点项目名字" value="">',
                    '<span class="btn-search-item"><i class="fa fa-search"></i></span>',
                '</div>',
                
                '<div class="border-top-1 bdc-e4e4e4 text-right mt-5 pt-10 item-footer">',
                    '<span>成本总价: <span class="sum fb">0</span> 元，</span>',
                    '<span>总售价: <span class="sum-sale-price fb">0</span> 元，</span>',
                    '<span>毛利: <span class="rate">0</span>%</span>',
                '</div>',
            '</ul>'
        ].join(''),

        // 初始化项目产品自动补全下拉框
        _initItemAutocomplete: function(){
            var me = this;

            me.$('.search-item').autocomplete({
                serviceUrl: '/admin/item/get_items_by_name',
                paramName: 'name',
                isLocal: false,
                triggerSelectOnValidInput: false,
                deferRequestBy: 300,
                transformResult: function(response) {
                    var data = JSON.parse(response),
                        result = [];

                    if(data){
                        result = $.Global.Utils.dictMapParse(data, me._modelMaps);
                    }
                    
                    return {
                        suggestions: result
                    };
                },
                onSelect: function(suggestion){
                    // 添加项目
                    me.addItem(suggestion);
                },
                formatResult: function(suggestion, value){
                    return String.format(
                        '<div class="suggestion-item">{0}{3}<span class="pull-right">{1} / {2}</span></div>', 
                        suggestion.value, 
                        suggestion.price,
                        suggestion.specText,
                        suggestion.smartDes
                    );
                }
            })
        },

        // 项目模板
        _itemTemplate: _.template([
            '<li class="pb-10 item-type-<%= item.itemType %>" data-item_id="<%= item.data %>">',
                '<div class="row">',
                    '<div class="col-sm-10 pr-0 col-xs-10">',
                        '<div class="input-group">',
                            '<span class="input-group-addon"><%= item.value %><%= item.smartDes %></span>',
                            '<input type="text" name="item-amounts" data-item_price="<%= item.price %>" data-item_sale_price="<%= item.salePrice %>" required class="form-control number item" value="<%= item.amount %>">',
                            '<input type="hidden" name="item-ids" value="<%= item.data %>">',
                            '<span class="input-group-addon"><%= item.specText %>, <span class="total-price" data-total_sale_price="<%= $.Global.Utils.formatPrice(item.salePrice * item.amount) %>"><%= $.Global.Utils.formatPrice(item.price * item.amount) %></span> 元</span></span>',
                        '</div>',
                    '</div>',
                    '<div class="col-sm-2 col-xs-2 text-right">',
                        '<a class="btn btn-danger btn-remove-item" title="删除该项目">X</a>',
                    '</div>',
                '</div>',
            '</li>'
        ].join('')),

        // 项目类型模版
        _itemTypeTemplate: _.template([
            '<% _.each(types, function(type){ %>',
            '<div class="fb fi pb-5 type-<%= type.value %>"><%= type.name %> ( 总价: <span class="sum-<%= type.value %>">0</span>, 总售价: <span class="sum-sale-price-<%= type.value %>">0</span> )</div>',
            '<% }) %>'
        ].join('')),

        // 初始化项目类型
        _initItemTypes: function(){
            var me = this;

            ajaxSend(
                "/admin/item/get_item_types", 
                {},
                function(data){
                    me._itemTypes = data;
                    $(me._itemTypeTemplate({'types': data})).insertAfter(me.$('.item-header'));
                    me._initItems(me._initItemIds);
                    me._loadItems(me._items, true);
                }
            );
        },

        // 加载项目
        _loadItems: function(items, clear){
            var me = this;

            // 是否清除已有项目
            if(clear){
                this.$(".items-view li").remove();
            }

            $.map(items, function(item){
                me.addItem(
                    $.Global.Utils.dictMap(item, me._modelMaps)
                );
            });
        },

        // 初始化项目
        _initItems: function(initItemIds){
            var me = this;

            $.map(initItemIds, function(itemId){
                ajaxSend(
                    "/admin/item/get_item_by_id", 
                    {'item_id': itemId},
                    function(data){
                        // 添加项目
                        me.addItem(
                            $.Global.Utils.dictMap(data, me._modelMaps)
                        );
                        
                        // me._loadItems(me._items, true);
                    }
                );
            });
        },

        // 删除项目
        _removeItem: function(sender){
            var target = $(sender.currentTarget);

            target.parents('li').remove();

            this.calculatePrice();
        },

        // 点击选中
        _focusItem: function(sender){
            var target = $(sender.currentTarget);

            target[0].select();
        },

        // 价格变动
        _changeAmount: function(sender){
            var target = $(sender.currentTarget),
                price = parseFloat(target.data("item_price")),
                salePrice = parseFloat(target.data("item_sale_price")),
                amount = parseFloat(target.val()),
                totalPrice = $.Global.Utils.formatPrice(
                    price * amount
                ),
                totalSalePrice = $.Global.Utils.formatPrice(
                    salePrice * amount
                );
            
            target.parents('li').find('.total-price').html(totalPrice);
            target.parents('li').find('.total-price').data('total_sale_price', totalSalePrice);
            this.calculatePrice();
        },

        // 计算分类总价
        _calculateTypePrice: function(){
            var me = this, allSalePrice = 0;

            $.map(me._itemTypes, function(itemType){
                var sum = 0, sumSalePrice = 0;

                $.map(me.$('.item-type-'+itemType.value+' .total-price'), function(price){
                    sum += parseFloat(price.innerHTML);
                    sumSalePrice += parseFloat($(price).data('total_sale_price'));
                });
                
                me.$('.sum-' + itemType.value).html($.Global.Utils.formatPrice(sum));
                me.$('.sum-sale-price-' + itemType.value).html($.Global.Utils.formatPrice(sumSalePrice));

                allSalePrice += sumSalePrice;
            });

            me.$('.sum-sale-price').html($.Global.Utils.formatPrice(allSalePrice));
            
        },

        events: {
            'click .btn-remove-item': '_removeItem',
            'click .item': '_focusItem',
            'input .item': '_changeAmount'
        },

        // 添加项目
        addItem: function(_data){
            
            var data = $.extend({
                    value: '',
                    data: '0',
                    price: 0,
                    salePrice: 0,
                    itemType: '1',
                    spec: '',
                    specText: '',
                    des: '',
                    amount: 0
                }, _data),

                _items = this.$('.items-view li'),
                temp = _items.filter(function(i){return _items.eq(i).data('item_id') == _data.data});

            // 是否已经存在
            if(temp.length == 0){
                
                $(this._itemTemplate({'item': data})).insertAfter(this.$('.type-' + data.itemType));

                this.calculatePrice();
            }

        },
        
        // 计算总价
        calculatePrice: function(){
            var sum = 0, rate = 0;

            this._calculateTypePrice();

            // 总价
            $.map(this.$('.total-price'), function(price){
                sum += parseFloat(price.innerHTML);
            });
            this.$('.sum').html($.Global.Utils.formatPrice(sum));

            // 计算毛利
            rate = this.totalSalePrice > 0 ? Math.round((1-sum/this.totalSalePrice)*10000)/100 : 0;
            this.$('.rate').html(rate);
        },

        // 批量加载项目
        loadItems: function(items){
            this._items = items;
        },

        initItems: function(initItemIds){
            this._initItemIds = initItemIds;
        },

        render: function(){
            this.$el.html(this._html);
            this._initItemAutocomplete();
            this._initItemTypes();
        }
    });

    /*
        项目详细信息组件
        主要用于显示套餐下的项目，订单下的项目
    */
    $.Global.ComponentView.ItemDetailView = Backbone.View.extend({
        el: '#item-detail-view',

        showSupplier: false,

        showItemImage: false,

        _items: [],

        _html: function(){
            var me = this;

            return [
            '<table class="table table-hover pr">',
                '<thead>',
                    '<tr>',
                        '<th>#</th>',
                        me.showItemImage ? '<th class="hidden-xs">产品图片</th>' : '<th class="hidden-xs">产品编号</th>',
                        '<th>产品名称</th>',
                        '<th>数量</th>',
                        '<th>规格</th>',
                        '<th class="hidden-xs">类别</th>',
                        me.showSupplier ? '<th>供货商</th>' : '',
                    '</tr>',
                '</thead>',
                '<tbody>',
                '</tbody>',
            '</table>'
            ].join('');
        },

        // 项目类型模版
        _itemTypeTemplate: _.template([
            '<% _.each(types, function(type){ %>',
            '<tr class="item_type item_type_<%= type.value %>">',
                '<td colspan="7" class="fb fi border-bottom-2 bdc-dddddd"><%= type.name %></td>',
            '</tr>',
            '<% }) %>'
        ].join('')),

        // 项目信息模版
        _itemTemplate: function(data){
            var me = this;
            return _.template([
                '<tr>',
                    '<td></td>',
                    me.showItemImage ? '<td class="hidden-xs pr"><img src="<%= img %>" class="w35 item-detail-small-img" /><img src="<%= img %>" class="w250 item-detail-big-img" /></td>' : '<td class="hidden-xs"><%= code %></td>',
                    '<td><%= name %><%= smart_des %></td>',
                    '<td><%= amount %></td>',
                    '<td><%= spec_str %></td>',
                    '<td class="hidden-xs"><%= item_type_str %></td>',
                    me.showSupplier ? '<td><%= supplier_name %></td>': '',
                '</tr>'
            ].join(''))(data)
        },

        // 初始化项目类型
        _initItemTypes: function(){
            var me = this;

            ajaxSend(
                "/admin/item/get_item_types", 
                {},
                function(data){
                    me.$('tbody').append(
                        me._itemTypeTemplate({'types': data})
                    );
                    me._loadItems(me._items);
                }
            );
        },

        // 设置编号
        _setIndex: function(){
            var trs = this.$('tbody>tr').filter(function(){return !$(this).hasClass('item_type')});
            
            $.map(trs, function(per, index){
                $(per).children().eq(0).html(index+1);
            });
        },

        // 加载项目
        _loadItems: function(items){
            var me = this;
            
            $.map(items, function(item){
                
                $(me._itemTemplate(item))
                .insertAfter(me.$('.item_type_' + item.item_type));
            });
            
            me._setIndex();
            setTimeout(function(){
                me._hideItemType();
            }, 100);
            
        },

        _hideItemType: function(){
            var me = this, 
                targets = $('.item_type');

            targets.filter(function(index){
                return targets.eq(index).next().hasClass('item_type');
            }).hide();

        },

        // 获取订单下的所有项目
        getItemsByOrderId: function(orderId){
            var me = this;

            ajaxSend(
                "/admin/order/get_items_of_order", 
                {'order_id': orderId},
                function(data){
                    me._loadItems(data);
                }
            );
        },

        // 获取套餐下的所有项目
        getItemsByMealId: function(mealId){
            var me = this;

            ajaxSend(
                "/admin/meal/get_items_of_meal", 
                {'meal_id': mealId},
                function(data){
                    me._loadItems(data);
                }
            );
        },

        // 加载项目
        loadItems: function(items){
            this._items = items;
        },

        render: function(){
            this.$el.html(this._html());
            this._initItemTypes();
        }
    });

    
    $.Global.Image = {
        version: '1.0.0',
        author: 'stranger',
        description: '图片控件'
    }
    /*
        全屏显示
    */
    $.Global.Image.FullImage = function(imageUrl){

        $('#full_image_modal').remove();

        var clientWidth = 0,
            height = 0,
            width = 0,
            html = [
                '<div class="modal fade text-center" id="full_image_modal">',
                    '<img style="max-width: 90%; transition: all 0.3s;" data-rotate="0" src="'+imageUrl+'" />',
                    '<span class="pf fa fa-times-circle-o co-ffffff pointer f40 close-img" style="right: 30px; top: 15px;"></span>',
                    '<span class="pf fa fa-share co-ffffff pointer f40 rotate-left" title="顺时针旋转" style="bottom: 30px; left: 45%;"></span>',
                    '<span class="pf fa fa-reply co-ffffff pointer f40 rotate-right" title="逆时针旋转" style="bottom: 30px; left: 55%;"></span>',
                '</div>'
            ].join(''),

            // 旋转图片
            changeRotate = function(flag){
                var target = $('#full_image_modal img'),
                    deg = parseInt(target.data('rotate'));

                // 旋转
                if(flag == true){
                    deg += 90;
                } else {
                    deg -= 90;
                }
                target.data('rotate', deg);

                target.css({
                    'transform': 'rotateZ('+deg+'deg)',
                    '-webkit-transform': 'rotateZ('+deg+'deg)'
                });

                // 宽度
                var tempWidth = 0,
                    rate = imgWidth / imgHeight;

                if( (Math.abs(deg)/90)%2 == 1 ) {
                    tempWidth = clientWidth < imgWidth ? clientWidth * rate : imgWidth;
                } else {
                    tempWidth = clientWidth < imgWidth ? clientWidth : imgWidth;
                }

                target.css({
                    width: tempWidth
                });

            },
            getImageSize = function(){

                // 计算图片
                var img = new Image();
                img.style.display = "none";
                img.onload = function(){
                    var marginTop = $(window).height() - img.height;
                        marginTop = marginTop > 0 ? marginTop / 2 : 0;

                    // 动态计算图片位置和大小
                    $('#full_image_modal img').css({
                        'marginTop': marginTop
                    });

                    clientWidth = $(window).width() * 0.9;
                    imgWidth = img.width;
                    imgHeight = img.height;
                }
                $('body').append(img);
                img.src = imageUrl;
            };


        $('body').append(html);

        // 关闭图片事件
        $('#full_image_modal .close-img')
        .on('click', function(){
            $('#full_image_modal').modal('hide');
        });
        $('.rotate-left').on('click', function(){
            changeRotate(true);
        });
        $('.rotate-right').on('click', function(){
            changeRotate(false);
        });

        $('#full_image_modal').modal('show');
        getImageSize();
    };

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

});