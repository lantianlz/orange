# -*- coding: utf-8 -*-


"""
@attention: 七牛客户端
@author: lizheng
@date: 2014-03-15
"""

from django.conf import settings
import StringIO
import logging
import json
import qiniu.io
import qiniu.rs

from common import utils


AK = 'z_k3BmEcJHZcrGjof_p7E4wcDvbh9_OXOU3DZbFS'
SK = 'Jwrj_cTFMbjlx4QH0xkSqrixTHAFPk98nQqp8DSU'

qiniu.conf.ACCESS_KEY = AK
qiniu.conf.SECRET_KEY = SK


def get_upload_token(img_key=None, img_type='avatar', scope='orange-img0'):
    if img_key:
        scope = '%s:%s' % (scope, img_key)
    if img_type == 'avatar':
        returnUrl = '%s/qiniu_img_return' % settings.MAIN_DOMAIN
    else:
        returnUrl = ''
    returnBody = ('{"user_id":$(x:user_id), "img_type":$(x:img_type), "key":$(key),  "hash":$(etag), "w":$(imageInfo.width), '
                  '"h":$(imageInfo.height), "bucket":$(bucket)}')

    policy = qiniu.rs.PutPolicy(scope=scope)
    if returnUrl:
        policy.returnUrl = returnUrl
    policy.returnBody = returnBody
    policy.insertOnly = 1
    uptoken = policy.token()
    return uptoken


def _resize_img(obj, dst_w=0, dst_h=0):
    ''' 
    等比压缩图片
    只给了宽或者高，或者两个都给了，然后取比例合适的 
    如果图片比给要压缩的尺寸都要小，就不压缩了 
    ''' 
    if dst_w or dst_h:
        from PIL import Image

        img = Image.open(obj)
        ori_w, ori_h = img.size
        width_ratio = height_ratio = None
        ratio = 1

        if (ori_w and ori_w > dst_w) or (ori_h and ori_h  > dst_h):
            if dst_w and ori_w > dst_w:
                width_ratio = float(dst_w) / ori_w
            if dst_h and ori_h > dst_h:
                height_ratio = float(dst_h) / ori_h
      
            if width_ratio and height_ratio:
                if width_ratio < height_ratio:
                    ratio = width_ratio
                else:
                    ratio = height_ratio
      
            if width_ratio and not height_ratio:
                ratio = width_ratio
      
            if height_ratio and not width_ratio:
                ratio = height_ratio
      
            new_width = int(ori_w * ratio)
            new_height = int(ori_h * ratio)
        else:
            new_width = ori_w
            new_height = ori_h
        
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        temp = StringIO.StringIO()
        img.save(temp, "gif")

        return temp
    else:
        return obj

def upload_img(file_data, img_type='other', file_name=None, dst_w=0, dst_h=0):

    # extra = qiniu.io.PutExtra()
    # extra.mime_type = "image/jpeg"

    # data 可以是str或readable对象
    if isinstance(file_data, (unicode, str)):
        data = StringIO.StringIO(file_data)
    else:
        data = StringIO.StringIO(file_data.read())

    # ============= 图片预处理 ===============
    data = _resize_img(data, dst_w, dst_h)
    # =======================================

    uptoken = get_upload_token(img_type=img_type)
    key = '%s_%s' % (img_type, file_name or utils.uuid_without_dash())
    ret, err = qiniu.io.put(uptoken, key, data)

    if err is not None:
        logging.error('upload_img error is:%s\n ret is %s' % (err, ret))
        return False, err

    key = ret.get('key', '')
    # 编辑器上传图片最大宽度为600
    if img_type == 'editor':
        key += '!600m0'
        # if int(ret.get('w', 0)) > 600:
        #     key += '!600m0'
    return True, key


def batch_delete(lst_names, bucket_name='orange-img0'):
    '''
    @note: 批量删除文件
    '''
    lst_path = []
    if not isinstance(lst_names, (list, tuple)):
        return False, 'lst_names error'
    for name in lst_names:
        lst_path.append(qiniu.rs.EntryPath(bucket_name, name))

    rets, err = qiniu.rs.Client().batch_delete(lst_path)
    if not [ret['code'] for ret in rets] == [200, ] * len(lst_path):
        return False, u'删除失败，%s\n%s' % (rets, err)
    return True, u'ok'

if __name__ == '__main__':
    get_upload_token()
