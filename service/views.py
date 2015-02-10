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
import commands
import redis
from PIL import Image
from django.core.servers.basehttp import FileWrapper

logger = logging.getLogger(__name__)
app_cfg = settings.app_cfg

(rhost,rport) = (settings.redis_host,settings.redis_port)
redis_cli = redis.Redis(host=rhost,port=rport)

(host,port,repl) = (settings.mongo_host,settings.mongo_port,settings.mongo_replicaset)
logger.debug( "mongodb_info::> %s ; %s ; %s" % (host,port,repl) )
conn = pymongo.MongoClient(host=host,port=int(port),replicaset=repl)
db = conn.fileserver

########################################
## private method 
########################################

def appendIndex(args):
	coll = db.fileindex
	if args.get('pk') and coll.find_one({'pk':args.get('pk')}) :
		logger.debug('[update] args = %s' % args)
		coll.remove({'pk':args.get('pk')})
	else:
		logger.debug('[insert] args = %s' % args)
	coll.insert(args)
	
def getIndex(args):
	coll = db.fileindex
	logger.debug('getIndex args = %s ' % args)
	return coll.find_one(args,{'_id':0})

def delIndex(args):
	coll = db.fileindex
	coll.remove(args)
	

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
	auth = args.get('auth')
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
	appendIndex({'pk':id,'path':output,'appid':appid,'file_type':file_type,'file_name':file_name,'ct':now,'auth':auth})
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

def check_token(token):
	'''
	校验token是否有效，token都是1次性的，所以通过时要删除token，防止重复使用
	'''
	if redis_cli.get('fileserver.'+token):
		redis_cli.delete('fileserver.'+token)
		logger.debug('check_token_return = True')
		return True			
	else:
		logger.debug('check_token_return = False')
		return False

def get_token(request):
	token = None
	if 'GET' == request.method :
		if request.GET.has_key('token'):
			token = request.GET.get('token')
	elif 'POST' == request.method :
		if request.POST.has_key('token'):
			token = request.POST.get('token')
	logger.debug('get_token_return = %s' % token)
	return token

############################################
## http handler
############################################

def token(request):
	'''
	对附件进行删除操作时，需要从此获取token先，然后才能删除
	只接收post请求，
	输入参数： appid, appkey
	输出：
		成功 {"success":true,"entity":{"token":"..."}}
		失败 {"success":false,"entity":{"reason":"..."}}
	'''
	try:
		if 'POST' == request.method:
			appid = request.POST.get('appid')
			appkey = request.POST.get('appkey')
			logger.debug("appid=%s ; appkey=%s ; app_cfg=%s" % (appid,appkey,app_cfg) )
			if appkey and app_cfg.has_key(appid) and appkey==app_cfg.get(appid).get('appkey') :
				# 校验通过
				token = uuid.uuid4().hex
				redis_cli.psetex("fileserver."+token,1000*60*60,'{"appid":"%s","appkey":"%s"}' % (appid,appkey))	
				return HttpResponse('{"success":true,"entity":{"token":"%s"}}' % token, content_type='text/json;charset=utf8')
			else:
				# 校验失败
				return HttpResponse('{"success":false,"entity":{"reason":"appkey_error"}}', content_type='text/json;charset=utf8')
		else:
			return HttpResponse('{"success":false,"entity":{"reason":"only_accept_post"}}', content_type='text/json;charset=utf8')
	except:
		return HttpResponse('{"success":false,"entity":{"reason":"error_params"}}', content_type='text/json;charset=utf8')


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
		if request.POST.has_key('file_name'):
			file_name = request.POST.get('file_name')
		else:
			file_name = my_file.name
		logger.debug('file_name==%s' % file_name)
		# 上传附件的应用名,如果是图片，此名称会对应一个单独的水印,通过 settings.watermark 来配置即可
		appid = request.POST.get('appid')
		# appid 和 appkey 要匹配，否则不能执行写操作
		appkey = request.POST.get('appkey')
		# 校验 appkey 
		if appkey and app_cfg.has_key(appid) and appkey==app_cfg.get(appid).get('appkey') :
			# 校验通过
			pass	
		else:
			# 校验失败
			return HttpResponse('{"success":false,"entity":{"reason":"appkey_error"}}', content_type='text/json;charset=utf8')

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
		auth = False
		logger.debug('request__post:: id=%s ; auth=%s' % (id,request.POST.get('auth')))
		if request.POST.has_key('auth') and request.POST.get('auth'):
			if 'true' == auth.lower() :
				auth = True	
		# 文件流
		sio = readFile(my_file)
		# 存储地址
		spath = genStorePath()
		
		handlerUpload(
			appid = appid,
			id = id,
			file_type = file_type,
			file_name = file_name,
			watermark = watermark,
			string_io = sio,
			output_path = spath,
			auth = auth
		)
		success['entity'] = {'id':id}
	else:
		success['success'] = False
		success['entity'] = {"reason":"only_accept_post"}

	rtn = json.dumps(success)
	logger.debug(rtn)
	return HttpResponse(rtn, content_type='text/json;charset=utf8')


def getFile(request,id):
	logger.debug("[get] method="+request.method+" ; id="+id)
	try:
		if request.GET.has_key('size'):
			size = request.GET.get('size')
		idx = getIndex({'pk':id})
		logger.debug("=======> idx = %s" % idx)
		if idx :
			if idx.get('auth'):	
				token = get_token(request)
				if token:
					if check_token(token):
						pass
					else:
						return HttpResponse("error_token",content_type="text/html ; charset=utf8")
				else:
					return HttpResponse("not_found_token",content_type="text/html ; charset=utf8")

			f = idx.get('path')
			filename = idx.get('file_name')
			wrapper = FileWrapper(file(f))
			if 'image' == idx.get('file_type'):
				response = HttpResponse(wrapper, content_type='text/plain;charset=utf8')
			else:	
				filename = idx.get('file_name')
				response = HttpResponse(wrapper,mimetype='application/octet-stream') 
				response['Content-Disposition'] = 'attachment; filename=%s' % filename.encode('utf8')
			response['Content-Length'] = os.path.getsize(f)
			response['Content-Encoding'] = 'utf-8'
			return response
		else:
			return HttpResponse("not_found",content_type="text/html ; charset=utf8")
	except Exception,e :
		#err = traceback.format_exc()
		#logger.info('======= ERROR ====== %s' % 'start')
		#logger.info('%s' % err)
		#logger.info('======= ERROR ====== %s' % 'end')
		logger.error(e)
		return HttpResponse("exception",content_type="text/html ; charset=utf8")

def delFile(request):
	logger.debug("<del> method="+request.method)
	try:
		if 'POST' == request.method :
			id = request.POST.get('id')
			logger.debug("[del] method="+request.method+" ; id="+id)
			idx = getIndex({'pk':id})
			logger.debug("=====> idx = %s" % idx)
			if idx.get('auth') : 
				token = get_token(request)
				if token:
					if check_token(token):
						pass
					else:
						success = '{"success":false,"entity":{"reason":"error_token"}}'
						logger.debug(id+"__"+success)
						return HttpResponse(success,content_type="text/json ; charset=utf8")
				else:
					success = '{"success":false,"entity":{"reason":"not_found_token"}}'
					logger.debug(id+"__"+success)
					return HttpResponse(success,content_type="text/json ; charset=utf8")
			else:
				if request.POST.has_key('appid') and request.POST.has_key('appkey'):
					appid,appkey = request.POST.get('appid'),request.POST.get('appkey')
					if app_cfg.get(appid) and appkey == app_cfg.get(appid).get('appkey'):
						pass
					else:
						success = '{"success":false,"entity":{"reason":"error_appkey"}}'
						logger.debug(id+"__"+success)
						return HttpResponse(success,content_type="text/json ; charset=utf8")
				else:
					success = '{"success":false,"entity":{"reason":"error_params"}}'
					logger.debug(id+"__"+success)
					return HttpResponse(success,content_type="text/json ; charset=utf8")
			f = idx.get('path')
			os.remove(f)
			delIndex({'pk':id})
			success = '{"success":true}'
			logger.debug(id+"__"+success)
			return HttpResponse(success,content_type="text/json ; charset=utf8")
		else:
			success = '{"success":false,"entity":{"reason":"only_accept_post"}}'
			logger.debug(id+"__"+success)
			return HttpResponse(success,content_type="text/json ; charset=utf8")
	except :
		success = '{"success":false,"entity":{"reason":"not_found"}}'
		logger.debug(id+"__"+success)
		return HttpResponse(success,content_type="text/json ; charset=utf8")

def infoFile(request,id):
	logger.debug("[del] method="+request.method+" ; id="+id)
	try:
		if request.GET.has_key('size'):
			size = request.GET.get('size')
		idx = getIndex({'pk':id})
		logger.debug("+++++++ idx = %s" % idx)
		success = {'success':True,'entity':idx}
		rtn = json.dumps(success)
		return HttpResponse(rtn,content_type="text/json ; charset=utf8")
	except :
		return HttpResponse('{"success":false}',content_type="text/json ; charset=utf8")


def doc2html(request,id):
	'''
	将id对应的文档转换成html，并返回给请求方
	'''
	logger.debug("[doc2html] method="+request.method+" ; id="+id)
	try:
		idx = getIndex({'pk':id})
		i = idx.get('path')
		o = '/tmp/%s.html' % id
		cmd = '/usr/bin/unoconv -o /tmp -f html %s' % (i)
		logger.debug('[doc2html] cmd=%s' % cmd)
		(status,output) = commands.getstatusoutput(cmd)
		logger.debug('[doc2html] status=%s ; output=%s' % (status,output))
		if status == 0 :
			rf = open(o,'r')
			html = rf.read()
			rf.close()
			success = {'success':True,'entity':{'html':html}}
			rtn = json.dumps(success)
			return HttpResponse(rtn,content_type="text/json ; charset=utf8")
		else:
			return HttpResponse('{"success":false,"entity":{"reason":"%s"}}' % (output),content_type="text/json ; charset=utf8")
	except Exception,e :
		logger.error(e)
		return HttpResponse('{"success":false,"entity":{"reason":"%s"}}' % (e),content_type="text/json ; charset=utf8")
