#/usr/bin/env python
#coding=utf8

from wand.image import Image
import os
import logging
logger = logging.getLogger(__name__)

# 缩放图片
# http://localhost:8000/fileserver/get/123456/resize(l=100)
# http://localhost:8000/fileserver/get/123456/resize(w=100,h=100)
# http://localhost:8000/fileserver/get/123456/resize(w=100)
# http://localhost:8000/fileserver/get/123456/resize(h=100)
def resize(l=None,w=None,h=None,path=None,nid=None):
    logger.debug('resize : l=%s,w=%s,h=%s,path=%s,nid=%s' % (l,w,h,path,nid))
    (dir, f) = os.path.split(path)
    # 最重要保存的文件路径
    # 要注意,这个文件如果已经存在,则进行修改操作,否则此文件从原图 克隆而来
    result_path = os.path.join(dir,nid)
    if os.path.exists(result_path):
        img = Image(filename=result_path)
    else:
        img_tmp = Image(filename=path).clone()
        img = img_tmp.clone()
        img_tmp.close()

    # 当传了最小边长时,将忽略 w 和 h 参数,然后按照原图的 size 找最短边参照 l 做等比缩放
    (ww,hh) = img.size
    if l:
        if l < ww or l < hh:
            if ww < hh :
                w = l
                h = int(float(w) / float(ww) * hh)
            else:
                h = l
                w = int(float(h) / float(hh) * ww)
        else:
            w = ww
            h = hh
    elif w and not h :
        # 按照宽等比缩放
        if w < ww :
            h = int(float(w) / float(ww) * hh)
        else:
            h = hh
            w = ww
    elif h and not w :
        # 按照高等比缩放
        if h < hh :
            w = int(float(h) / float(hh) * ww)
        else:
            h = hh
            w = ww
    elif w and h :
        # 按照宽高缩放
        if w > ww : w = ww
        if h > hh : h = hh
    img.resize(width=w,height=h)
    img.save(filename=result_path)
    img.close()
    logger.debug("(ww=%s,hh=%s) -> (w=%s,h=%s) ; %s" % (ww,hh,w,h,result_path))

# 剪切图片
# http://localhost:8000/fileserver/info/123456/crop(w=500)/
# http://localhost:8000/fileserver/info/123456/crop(h=500)/
# http://localhost:8000/fileserver/info/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/info/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/info/123456/crop(x=100,y=200,w=500,h=800)/
# http://localhost:8000/fileserver/info/123456/resize(w=400,h=300)&crop(x=100,y=200,w=500,h=800)/
def crop(l=None,x=0,y=0,w=None,h=None,path=None,nid=None):
    '''
    :param l: 当传了最小边长时,将忽略 w 和 h 参数,然后按照原图的 size 找最短边参照 l 计算出宽高比例
    :param x: 以左上角为 O, x 轴 ; (x,y) 为剪切的起点
    :param y: 以左上角为 O, y 轴 ; (x,y) 为剪切的起点
    :param w: 长
    :param h: 高
    :param path: 原图地址
    :param nid: 图片唯一id,保存时使用
    :return:

    当 x,y 不传时,按照图片的宽高比例进行剪切,如果是宽图,那么 y = 0,如果是长图则 x = 0
    然后 按照 l 或者 (w,h) 计算出 x 或 y,并进行剪切
    '''
    (dir, f) = os.path.spli(path)
    # 最重要保存的文件路径
    # 要注意,这个文件如果已经存在,则进行修改操作,否则此文件从原图 克隆而来
    result_path = os.path.join(dir,nid)
    if os.path.exists(result_path):
        img = Image(filename=result_path)
    else:
        img_tmp = Image(filename=path).clone()
        img = img_tmp.clone()
        img_tmp.close()

    ww,hh = img.size
    # TODO

    img.crop(left=x,top=y,width=w,height=h)
    img.resize(width=w,height=h)
    img.save(filename=result_path)
    img.close()


