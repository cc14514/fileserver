# !/usr/bin/env python 
# coding=utf-8


DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Django settings for fileserver project.

if DEBUG :
###############################################
# 开发环境
###############################################
	redis_host = '192.168.12.212'
	redis_port = 6379
	
	# 存储图片索引的 mongodb 
	mongo_port = '27017'
	mongo_host = '192.168.12.213'
	mongo_replicaset = 'part1'
	
	# 存放图片的跟目录
	root_path = '/app'
	
	# 默认的水印图片
	watermark_def = '/app/watermark_test.png'
	# 存放 appid 对应的 appkey 和水印文件
	app_cfg = {
		'admin':{
			'appkey':'lancefox', # appkey 相当于密码
		}
	}
	
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql', 
			'NAME': 'db_emsg', 
			'USER': 'root',
			'PASSWORD': '123456',
			'HOST': '192.168.12.213',  
			'PORT': '3306',
		}
	}
	
	ALLOWED_HOSTS = []

else:
###############################################
# 生产环境
###############################################
	redis_host = '192.168.12.212'
	redis_port = 6379
	
	# 存储图片索引的 mongodb 
	mongo_port = '27017'
	mongo_host = '192.168.12.213'
	mongo_replicaset = 'part1'
	
	# 存放图片的跟目录
	root_path = '/app'
	
	# 默认的水印图片
	watermark_def = '/app/watermark_test.png'
	# 存放 appid 对应的 appkey 和水印文件
	app_cfg = {
		'admin':{
			'appkey':'lancefox', # appkey 相当于密码
		}
	}
	
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.', 
	        'NAME': '',                      
	        'USER': '',
	        'PASSWORD': '',
	        'HOST': '',                      
	        'PORT': '',         
	    }
	}
	
	ALLOWED_HOSTS = []



ADMINS = ()
MANAGERS = ADMINS


TIME_ZONE = 'Asia/Chongqing'

LANGUAGE_CODE = 'zh-cn'

FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ''

MEDIA_URL = ''

STATIC_ROOT = '/app/static'

STATIC_URL = '/static/'

import os.path as op
STATICFILES_DIRS = (
    op.join(op.dirname(op.dirname(__file__)),'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'u8_58zr6rjgd-qhicj#w7#jq*-*4%&%@jt=7&b!f+zi7#o0m8%'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'fileserver.urls'

WSGI_APPLICATION = 'fileserver.wsgi.application'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'service',
    'fileserver'
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
        },
	},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter':'simple'
		},
		'file':{
			'level':'DEBUG',
			'class':'logging.FileHandler',
			'filename':'/tmp/fileserver.log',
			'formatter':'verbose',
		}
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
		'service.views':{
            'handlers': ['file','console'],
            'level': 'DEBUG',
            'propagate': True,
		}
    }
}

