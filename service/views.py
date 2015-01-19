#!/usr/bin/env python
#coding=utf-8

# Create your views here.
from django.http import HttpResponse
from django.http import HttpRequest
import time 
import json
import uuid
import pymongo
import logging
import traceback
import os
import StringIO
import fileserver.settings as settings
from PIL import Image
from django.core.servers.basehttp import FileWrapper

logger = logging.getLogger(__name__)
app_cfg = settings.app_cfg

#(host,port,repl) = (settings.mongo_host,settings.mongo_port,settings.mongo_replicaset)
#logger.debug( "mongodb_info::> %s ; %s ; %s" % (host,port,repl) )
#conn = pymongo.MongoClient(host=host,port=int(port),replicaset=repl)
#db = conn.fileserver
#coll = db.fileindex

def appendIndex(args):
	#coll.insert(args)
	pass
	
def getIndex(args):
	#return coll.find_one(args,{'_id':0})
	pass

def resizeImg(img,width):
	'''
	按比例缩放图片，必须指定新的宽度
	'''
	src_width,src_height = img.size
	bl = float(width) / src_width
	height = src_height * bl
	rtn = img.resize((int(width),int(height)))
	img.close()
	return rtn
def handlerUpload(**args):
	logger.debug(args)
	id = args.get('id')
	output_path = args.get('output_path')
	output = os.path.join(output_path,id)
	string_io = args.get('string_io')
	appid = args.get('appid')
	file_type = args.get('file_type')
	file_name = args.get('file_name')
	watermark = args.get('watermark')
	if 'image' == file_type :
		img = Image.open(string_io)
		logger.info("_______"+img.format)
		if watermark :
			cfg = app_cfg.get(appid)
			# 加水印
			wp = settings.watermark_def
			if cfg and cfg.has_key('watermark'):
				w = cfg.get('watermark')
				if w and os.path.exists(w):
					wp = w
			wp_img = Image.open(wp)
			logger.debug("wp_mode=%s" % wp_img.mode)
			# 水印尺寸
			wp_width,wp_height = wp_img.size
			# 原图尺寸
			img_width,img_height = img.size
			(r,g,b,a) = wp_img.split()
			# todo 右下角完美贴合，并且保证水印的高度比例为30%
			# 水印高度与原图的比例不能超过30%，如果超过则要将水印缩小到原图的30%高度
			bl = 0.3	
			if img_height * bl < wp_height:
				wp_img = resizeImg(wp_img,int(img_width*bl))
				wp_width,wp_height = wp_img.size	
				(r,g,b,a) = wp_img.split()
			box = (img_width-wp_width,img_height-wp_height)
			logger.debug("wp_img_size=%s ; src_img_size=%s" % (wp_img.size,img.size))
			logger.debug("box=%s ; mask=%s" % (box,a))
			img.paste(wp_img,box=box,mask=a)	
			img.save(output,img.format)
			wp_img.close()
		else:
			# 不加水印
			img.save(output,img.format)
		img.close()
	else:
		output_stream = open(output,'w')
		output_stream.write(string_io.read())
		output_stream.flush()
		output_stream.close()
		string_io.close()
	now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	# 创建索引到 mongodb
	appendIndex({'pk':id,'path':output,'appid':appid,'file_type':file_type,'file_name':file_name,'ct':now})
	string_io.close()

def genStorePath():
	base = settings.root_path
	d = time.strftime('%Y/%m/%d',time.localtime(time.time()))
	sp = os.path.join(base,d)
	if not os.path.exists(sp):
		os.makedirs(sp)
	return sp

def readFile(f):
	'''
	将http传递过来的附件从 
	django.core.files.uploadedfile.InMemoryUploadedFile 类型转换成
	StringIO 类型,指针拨到文件头，并返回 sio 对象
	'''
	sio = StringIO.StringIO()
	for chunk in f.chunks():
		sio.write(chunk)
	sio.seek(0)
	return sio




def upload(request):
	'''
	附件上传 
		<form action="http://localhost:8000/fileserver/upload" method="POST" enctype="multipart/form-data" >
			<!-- 上传附件的应用名,如果是图片，此名称会对应一个单独的水印,通过 settings.watermark 来配置即可 -->
			<p>appid:<input type="text" name="appid" value="test" /></p>
			<!-- 口令 -->
			<p>appkey:<input type="text" name="appkey" value="test" /></p>
			<!-- 附件id，如果为空则服务端产生id并返回给客户端，如果非空并且服务器上有这个id对应的附件，则会覆盖此附件；-->
			<p>appkey:<input type="text" name="appkey" value="test" /></p>
			<!-- 附件类型，file / image 文件或 image，默认 image -->
			<p>file_type:<input type="text" name="file_type" value="image" /></p>
			<!-- # 是否加水印, 如果 file_type=image 则默认 true,可选值 true / false -->
			<p>watermark:<input type="text" name="watermark" value="true" /></p>
			<!-- 附件 -->
			<p>file:<input type="file" name="file" /></p>
		</form>
	'''
	success = {'success':True}
	if 'POST' == request.method and request.FILES:
		# 附件的流
		my_file = request.FILES['file']
		logger.debug('file_name==%s' % my_file.name)
		# 上传附件的应用名,如果是图片，此名称会对应一个单独的水印,通过 settings.watermark 来配置即可
		appid = request.POST.get('appid')
		# appid 和 appkey 要匹配，否则不能执行写操作
		appkey = request.POST.get('appkey')
		# 附件id，如果为空则服务端产生id并返回给客户端，如果非空并且服务器上有这个id对应的附件，则会覆盖此附件；
		id = uuid.uuid4().hex
		if request.POST.has_key('id') and request.POST.get('id') :
			id = request.POST.get('id')
		# 附件类型，file / image 文件或 image，默认 image
		file_type = 'image'
		if request.POST.has_key('file_type') :
			file_type = request.POST.get('file_type')
		# 是否加水印, 如果 file_type=image 则默认 True
		watermark = True
		if request.POST.has_key('watermark') and 'false' == request.POST.get('watermark'):
			watermark = False
		# 文件流
		sio = readFile(my_file)
		# 存储地址
		spath = genStorePath()
		
		handlerUpload(
			appid = appid,
			id = id,
			file_type = file_type,
			file_name = my_file.name,
			watermark = watermark,
			string_io = sio,
			output_path = spath
		)
		success['entity'] = {'id':id}
	else:
		success['success'] = False

	rtn = json.dumps(success)
	logger.debug(rtn)
	return HttpResponse(rtn, content_type='text/json;charset=utf8')


def getFile(request,id):
	logger.debug("method="+request.method+" ; id="+id)
	try:
		if request.GET.has_key('size'):
			size = request.GET.get('size')
		idx = getIndex({'pk':id},{'_id':0})
		logger.debug("+++++++ %s" % idx)
		if idx :
			f = idx.get('path')
			wrapper = FileWrapper(file(f))
			response = HttpResponse(wrapper, content_type='text/plain;charset=utf8')
			response['Content-Length'] = os.path.getsize(f)
			response['Content-Encoding'] = 'utf-8'
			return response
		else:
			return HttpResponse("not_found",content_type="text/html ; charset=utf8")
	except :
		return HttpResponse("not_found",content_type="text/html ; charset=utf8")
