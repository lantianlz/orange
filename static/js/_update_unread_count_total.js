$(function(){
    function loop()
    {
        get_unread_count_total();
        setTimeout(loop, 60000);
    }
    loop();
});


function get_unread_count_total()
{
    var url = '/message/get_unread_count_total';
    ajaxSend(url, '', get_unread_count_total_callback, 'GET');
}


function get_unread_count_total_callback(data)
{
    var unread_count_total = 0;
    for(var key in data)
    {
        unread_count_total += data[key];
        $('#unread_count_total_nav_' + key).html(data[key]);
        if(data[key] > 0)
        {
            $('#unread_count_total_nav_' + key).show();
        }
        else
        {
            $('#unread_count_total_nav_' + key).hide();
        }
    }
    if(unread_count_total > 0)
    {
        $('#unread_count_total_nav_show').html(unread_count_total).show();
        $('#unread_count_total_nav_none').hide();
        document.title = '收到 ' + unread_count_total + ' 条新消息';
    }
    else
    {
        $('#unread_count_total_nav_none').show();
        $('#unread_count_total_nav_show').hide();
    }

}

