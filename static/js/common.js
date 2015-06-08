/**
 * @attention 通用ajax操作封装
 * @date 2012-12-27
 */

/*---------------------------------------------------------ajax操作部分-------------------------------------------------------------------------------*/

var jQ = $;
var g_debug = false;

function ajaxSend(urlIn, postData, callbackFunc, methodIn, dataType, dict_vars) {
	/**
	 * @attention:			通用的发送ajax请求的方法
	 * @param urlIn:		传入的url
	 * @param postData:		传送数据
	 * @param callbackFunc:	执行成功后执行的方法
	 * @param methodIn:		传输方法，默认为POST
	 * @param flag:			保留字段，不用赋值
	 * @author:	 			lizheng 2010-12-21
	 */
	var params = {
		url: urlIn,
		data: postData || '',
		type: methodIn || 'POST',
		success: successFun,
		error: function(request, textStatus, errorThrown) {
			//								alert(textStatus);
			//								alert(errorThrown);
			if (request.responseText != 'need_login' && request.status == 200 && dataType != 'jsonp' && g_debug) {
				if (g_debug) {
					alert('返回数据格式于指定的data_type:' + (dataType || 'json') + '不符!:  ' + request.responseText);
				}
			}
		},
		dataType: dataType || 'json',
		cache: false,
		global: true,
		//自定义参数，替代全局参数
		ajax_func_flag: false,
		custom_func: callbackFunc
	}
	if (dict_vars) {
		for (var key in dict_vars) {
			params[key] = dict_vars[key];
		}
	}
	//	alert(params.toSource());
	jQ.ajax(params);
}


function successFun(data, textStatus) {
	/**
	 * @attention:			执行成功调用的方法
	 * @param data:			ajax返回的数据
	 * @param textStatus:	成功的状态
	 * @author:	 			lizheng 2010-12-21
	 */
	try {
		//成功后执行方法
		if (this.ajax_func_flag && data) {
			parseJson(data);
		} else if (this.custom_func) {
			this.custom_func(data);
		}
	} catch (e) {
		alert(e);
	}
}


jQ(document).ajaxError(function(event, request, settings) {
	/**
	 * @attention:	请求错误
	 * @author:	 	lizheng 20100805
	 */
	if (request.status == 0 && g_debug) {
		//alert('网络无法访问');
	}
	if (request.status != 200 && request.status != 0 && g_debug) {
		var height = jQ(window).height() < 800 ? 800 : jQ(window).height();
		var width = jQ(window).width() < 1440 ? 1440 : jQ(window).width();
		var win = window.open('', '', 'width=' + width + ', height=' + height + ', scrollbars=yes');
		win.document.write(request.responseText);
		win.focus();
	}
})


jQ(document).ajaxSend(function() {
	/**
	 * @attention:	请求准备开始执行的全局方法
	 * @author:	 	lizheng 2010-12-21
	 */
	if (window.g_ajax_processing_obj_id) {
		show_ajax_processing();
	}
})


jQ(document).ajaxComplete(function(event, request, settings) {
	/**
	 * @attention:	请求stop结束后执行的全局方法
	 * @author:	 	lizheng 2010-12-21
	 */
	if (request.responseText == 'need_login' || request.responseText == 'perm_refuse') {
		$.Global.Notice.ErrorTopNotice('请先登录');
		// window.location = login_url;
	}
	if (request.responseText == 'need_staff') {
		$.Global.Notice.ErrorTopNotice('需要管理员权限才能执行');
	}
	
	if (request.responseText == 'permission_denied') {
		$.Global.Notice.ErrorTopNotice('权限不足！');
	}
	
	if (window.g_ajax_processing_obj_id) {
		hide_ajax_processing();
	}
})


function show_ajax_processing() {
	/**
	 * @attention:显示ajax等待
	 */
	var obj = jQ('#' + g_ajax_processing_obj_id);
	obj.hide();
	obj.next('img').remove();
	obj.after(jQ('<img  src="' + MEDIA_URL + '/img/loading.gif" alt="......" />'));
}


function hide_ajax_processing() {
	/**
	 * @attention:隐藏ajax等待
	 */
	var obj = jQ('#' + g_ajax_processing_obj_id);
	if (obj) {
		obj.show();
		obj.next('img').remove();
	}
	g_ajax_processing_obj_id = '';
}

/*---------------------------------------------------------通用操作部分-------------------------------------------------------------------------------*/


function divCenter(DivId) {
	/**
	 * @author: lizheng
	 * @date: 2010-11-15
	 * @des: 使元素在当前窗口的显示中绝对居中，包含x轴或者y轴的滚动条在内
	 * @param DivId: 元素Id
	 */
	var hideFlag = jQ('#' + DivId).is(':hidden'); //隐藏的话先显示出来，因为offset属性依赖于元素是否显示
	hideFlag ? jQ('#' + DivId).show() : null;

	jQ('#' + DivId).css({
		left: 0,
		top: 0
	});
	jQ('#' + DivId).css({
		bottom: '',
		right: ''
	})
	var left = (jQ(window).width() - jQ('#' + DivId).outerWidth()) / 2 + jQ(window).scrollLeft();
	var top = (jQ(window).height() - jQ('#' + DivId).outerHeight()) / 2 + jQ(window).scrollTop();
	left = left < 0 ? 0 : left;
	top = top < 0 ? 0 : top;
	jQ('#' + DivId).offset({
		left: left,
		top: top
	});

	hideFlag ? jQ('#' + DivId).hide() : null;
}


function fullDiv(divId) {
	/**
	 * @author: lizheng
	 * @date: 2010-11-15
	 * @des: 使元素铺满全屏
	 * @param DivId: 元素Id
	 */

	var height = jQ(document).height();
	var width = jQ(document).width();
	jQ('#' + divId).height(height).width(width);
}

/*--------------------------------------------------------弹出检测层-----------------------------------------------------------*/
var g_timeout;

function showError(target, errorMsg) {
	/*
	 * @attention:		显示检测错误信息
	 * @param target:	检测的对象
	 * @param errorMsg：	提示信息
	 * @author:			copy from check.js 20100730
	 */

	//得到坐标
	var target = jQ(target);
	var sprint = target.offset();
	var targetHeight = target.outerHeight();

	jQ('#divErrorMsg').html(errorMsg);
	var left = jQ('#divError').width() / 2 - target.outerWidth() / 2;
	jQ('#divError').css("display", "block").offset({
		left: sprint.left - left,
		top: sprint.top + parseFloat(targetHeight)
	});

	window.clearTimeout(g_timeout);

	//4秒时候自动关闭
	g_timeout = setTimeout(function() {
		if (jQ('#divError').css("display") == "block")
			jQ('#divError').css("display", "none");
	}, 4000);

	target.focus();
}

/*--------------------------弹出删除确认层相关公用js，可以独立出去-----------------------*/
function DeleteConfirm(text) {
	/**
	 *@attention:类
	 *@author: lizheng
	 *@date: 2010-01-23
	 */
	if (text) {
		jQ('#delete_confirm_text_info').text(text);
	}
	this.showUi = function(obj) {
		var obj = jQ(obj);
		var objDiv = jQ('#delete_confirm_div_id');
		objDiv.stop(true, true);
		var offset = obj.offset();
		var top = offset.top - objDiv.outerHeight();
		var left = offset.left - objDiv.outerWidth() / 2 + obj.outerWidth() / 2;
		objDiv.show().offset({
			'left': left,
			'top': top
		}).hide();
		objDiv.show('normal', function() {
			setTimeout(function() {
				jQ('#sure_confirm_id').focus()
			}, 100)
		})
	}

	this.hideUi = function() {
		var objDiv = jQ('#delete_confirm_div_id');
		objDiv.hide('normal')
	}
}

/*-------------------------end 弹出删除层相关公用js----------------------------------*/

/*--------------------------文字内容加1或者减1的动画操作--------------------------*/
function animateFontSize(obj, type) {
	/**
	 *@attention: 文字内容加1或者减1的动画操作
	 *@param obj: 文字对象
	 *@param type: 类型，0：加1， 1：减1
	 *@author: lizheng
	 *@date: 2010-01-23
	 */
	var obj = jQ(obj);
	var fontSize = obj.css('font-size');
	var count = parseInt(obj.text());
	count = parseInt(type) == 0 ? count + 1 : count - 1;
	obj.animate({
		'font-size': '0px'
	}, {
		'duration': 'fast',
		'complete': function() {
			obj.text(count);
			obj.animate({
				'font-size': fontSize
			}, 'slow');
		}
	});
}
/*--------------------------end文字内容加1或者减1的动画操作-----------------------*/

/*--------------------------文本框根据内容自动适应高度--------------------------*/
jQ.fn.autosize = function() {
	/**
	 * @attention:扩展jquery，自动适用textarea的高度
	 * @author: lizheng
	 * @date: 2010-01-23
	 */
	jQ(this).height('0px');
	var setheight = jQ(this).get(0).scrollHeight;
	if (jQ(this).attr("_height") != setheight) {
		jQ(this).height(setheight).attr("_height", setheight);
	} else {
		jQ(this).height(jQ(this).attr("_height") + 'px');
	}
}
/*--------------------------end文本框根据内容自动适应高度--------------------------*/


/*--------------------------end提示成功信息后隐藏--------------------------*/
function CommonCoverDiv() {
	/**
	 * @attention:通用的遮盖层类
	 * @author: lizheng
	 * @date: 2011-02-14
	 */

	//创建
	this.create = function() {
		var existDiv = jQ('#common_cover_div_id');
		if (existDiv.length != 0) {
			existDiv.remove();
		}
		var div = jQ('<div id="common_cover_div_id"></div>');
		jQ('body').append(div);
		fullDiv('common_cover_div_id');
	}

	//删除
	this.remove = function() {
		jQ('#common_cover_div_id').remove();
	}
}


function common_callback(data) {
	if (data['errcode'] == '0') {
		$.Global.SuccessTopNotice('操作成功!页面即将刷新');
		
		window.setTimeout(function(){
            window.location.reload();
        }, 2000)
	} else {
		$.Global.ErrorTopNotice(data['errmsg']);
	}
}


function register_shortcut(obj, click_obj, enter_or_ctrlenter) {
	/**
	 * @attention:通用注册快捷键
	 */
	obj = jQ(obj);
	enter_or_ctrlenter = enter_or_ctrlenter || 'ctrlenter';
	obj.keydown(function(e) {
		if ((enter_or_ctrlenter == 'ctrlenter' && e.ctrlKey && e.keyCode == 13) || (enter_or_ctrlenter == 'enter' && e.keyCode == 13)) {
			jQ(click_obj).click();
		}
	})
}


function getQueryStringRegExp(name) {
	/**
	 * @attention:获取url中的参数
	 */
	var reg = new RegExp("(^|\\?|&)" + name + "=([^&]*)(\\s|&|$)", "i");
	if (reg.test(location.href)) {
		return unescape(RegExp.$2.replace(/\+/g, " "));
	}
	return "";
};