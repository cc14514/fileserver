# /usr/bin/env python
# coding=utf8

from wand.image import Image
import os
import logging

logger = logging.getLogger(__name__)


# 缩放图片
# http://localhost:8000/fileserver/get/123456/resize(l=100)
# http://localhost:8000/fileserver/get/123456/resize(w=100,h=100)
# http://localhost:8000/fileserver/get/123456/resize(w=100)
# http://localhost:8000/fileserver/get/123456/resize(h=100)
def resize(l=None, w=None, h=None, path=None, nid=None):
    '''
    缩放图片
    :param l: 当传了最小边长时,将忽略 w 和 h 参数,然后按照原图的 size 找最短边参照 l 做等比缩放
    :param w: 要缩放的目标宽度
    :param h: 要缩放的目标高度
    :param path: 原图地址
    :param nid: 图片唯一id,保存时使用
    :return:
    '''
    logger.debug('resize : l=%s,w=%s,h=%s,path=%s,nid=%s' % (l, w, h, path, nid))
    (_dir, f) = os.path.split(path)
    # 最重要保存的文件路径
    # 要注意,这个文件如果已经存在,则进行修改操作,否则此文件从原图 克隆而来
    result_path = os.path.join(_dir, nid)
    if os.path.exists(result_path):
        img = Image(filename=result_path)
    else:
        img_tmp = Image(filename=path).clone()
        img = img_tmp.clone()
        img_tmp.close()

    # 当传了最小边长时,将忽略 w 和 h 参数,然后按照原图的 size 找最短边参照 l 做等比缩放
    (ww, hh) = img.size
    if l:
        if l < ww or l < hh:
            if ww < hh:
                w = l
                h = int(float(w) / float(ww) * hh)
            else:
                h = l
                w = int(float(h) / float(hh) * ww)
        else:
            w = ww
            h = hh
    elif w and not h:
        # 按照宽等比缩放
        if w < ww:
            h = int(float(w) / float(ww) * hh)
        else:
            h = hh
            w = ww
    elif h and not w:
        # 按照高等比缩放
        if h < hh:
            w = int(float(h) / float(hh) * ww)
        else:
            h = hh
            w = ww
    elif w and h:
        # 按照宽高缩放
        if w > ww: w = ww
        if h > hh: h = hh
    img.resize(width=w, height=h)
    img.save(filename=result_path)
    img.close()
    logger.debug("resize : (ww=%s,hh=%s) -> (w=%s,h=%s) ; %s" % (ww, hh, w, h, result_path))


# 剪切图片
# http://localhost:8000/fileserver/get/123456/crop(w=500)/
# http://localhost:8000/fileserver/get/123456/crop(h=500)/
# http://localhost:8000/fileserver/get/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/get/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/get/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/get/123456/resize(w=400,h=300)&crop(x=100,y=200,w=500,h=800)/
def crop(l=None, x=None, y=None, w=None, h=None, path=None, nid=None):
    '''
    当 x,y 不传时,按照图片的宽高比例进行剪切,如果是宽图,那么 y = 0,如果是长图则 x = 0
    然后 按照 l 或者 (w,h) 计算出 x 或 y,并进行剪切

    :param l: 当传了最小边长时,将忽略 w 和 h 参数,然后按照原图的 size 找最短边参照 l 计算出宽高比例
    :param x: 以左上角为 O, x 轴 ; (x,y) 为剪切的起点
    :param y: 以左上角为 O, y 轴 ; (x,y) 为剪切的起点
    :param w: 长
    :param h: 高
    :param path: 原图地址
    :param nid: 图片唯一id,保存时使用
    :return:
    '''
    logger.debug('crop : l=%s,w=%s,h=%s,x=%s,y=%s,path=%s,nid=%s' % (l, w, h, x, y, path, nid))
    (_dir, f) = os.path.split(path)
    # 最重要保存的文件路径
    # 要注意,这个文件如果已经存在,则进行修改操作,否则此文件从原图 克隆而来
    result_path = os.path.join(_dir, nid)
    if os.path.exists(result_path):
        img = Image(filename=result_path)
    else:
        img_tmp = Image(filename=path).clone()
        img = img_tmp.clone()
        img_tmp.close()

    ww, hh = img.size
    if l:
        if l < min(ww, hh):
            h = w = l
        else:
            h = w = min(ww, hh)
        if not x:
            x = int(float(ww - w) / float(2))
        if not y:
            y = int(float(hh - h) / float(2))

    if not x: x = 0
    if not y: y = 0
    if (w and w > (ww - x)) or not w: w = ww - x
    if (h and h > (hh - y)) or not h: h = hh - y

    img.crop(left=x, top=y, width=w, height=h)
    img.save(filename=result_path)
    img.close()
    logger.debug("crop : (ww=%s,hh=%s) -> (x=%s,y=%s,w=%s,h=%s) ; %s" % (ww, hh, x, y, w, h, result_path))


# http://localhost:8000/fileserver/get/123456/container(w=400,h=300)/
def container(w=None, h=None, path=None, nid=None):
    '''
    原图自适应的缩放到容器规格对应的尺寸上
    :param w: 图片容器的最大长度
    :param h: 图片容器的最大高度
    :param path: 原图地址
    :param nid: 图片唯一id,保存时使用
    :return:
    '''
    logger.debug('container : w=%s,h=%s,path=%s,nid=%s' % (w, h, path, nid))
    (_dir, f) = os.path.split(path)
    # 最重要保存的文件路径
    # 要注意,这个文件如果已经存在,则进行修改操作,否则此文件从原图 克隆而来
    result_path = os.path.join(_dir, nid)
    if os.path.exists(result_path):
        img = Image(filename=result_path)
    else:
        img_tmp = Image(filename=path).clone()
        img = img_tmp.clone()
        img_tmp.close()

    # 初始化目标宽高
    _w = _h = None

    ww, hh = img.size
    if ww > hh:
        # 宽图 : 按照宽度等比缩放, w
        if ww > w:
            # 当原图的宽度,大于容器宽度时,等比缩放到容器宽度
            _w = w
            _h = int(float(w) / float(ww) * float(hh))
            img.resize(width=_w,height=_h)
            if _h > h:
                img.crop(left=0,top=int( float(_h-h)/2.0 ),width=_w,height=h)
    else:
        # 长图 : 按照高度等比缩放, h
        if hh > h:
            # 当原图的高度,大于容器高度时,等比缩放到容器高度
            _h = h
            _w = int(float(h) / float(hh) * float(ww))
            img.resize(width=_w,height=_h)
            if _w > w:
                img.crop(top=0,left=int( float(_w-w)/2.0 ),width=w,height=_h)

    img.save(filename=result_path)

    log_w,log_h = img.size
    logger.debug("container : ww=%s,hh=%s --final--> ww=%s,hh=%s ; path=%s" % (ww,hh,log_w,log_h,result_path) )
    img.close()



