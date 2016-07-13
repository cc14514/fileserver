# !/usr/bin/env python 
# coding=utf-8


import os
import os.path as op

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    ###############################################
    # 开发环境
    ###############################################

    # 当前节点所关联的下载服务，nginx＋静态资源 方式搭建,
    # 下载文件时，用 http://current_node/dir/fid 的方式
    # 所以上传文件时需要把 current_node 放入 index 中
    current_node = '192.168.0.214'

    redis_host = '192.168.0.214'
    redis_port = 6379

    # 存储图片索引的 mongodb
    mongo_port = '27017'
    mongo_host = '192.168.0.214'
    mongo_replicaset = 'part1'

    # 显示图片时,需要用 nginx 来返回静态资源
    # nginx config part
    #
    #location ~* '\d{4}/\d{2}/\d{2}' {
    #    root   /tmp/fileserver;
    #    index  index.html index.htm;
    #}

    # 存放图片的跟目录
    root_path = '/tmp/fileserver'

    # 默认的水印图片
    watermark_def = '/home/appusr/var/etc/fileserver/def.png'
    # 存放 appid 对应的 appkey 和水印文件

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'db_emsg',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': '192.168.0.214',
            'PORT': '3306',
        }
    }

    ALLOWED_HOSTS = []

else:
    ###############################################
    # 生产环境
    ###############################################

    # 当前节点所关联的下载服务，nginx＋静态资源 方式搭建,
    # 下载文件时，用 http://current_node/dir/fid 的方式
    # 所以上传文件时需要把 current_node 放入 index 中
    node = '202.85.221.165'

    redis_host = '192.168.2.100'
    redis_port = 6379

    # 存储图片索引的 mongodb
    mongo_port = '27017'
    mongo_host = '192.168.2.100'
    mongo_replicaset = 'lc'

    # 存放图片的跟目录
    root_path = '/home/appusr/var/lib/fileserver'

    # 默认的水印图片
    watermark_def = '/home/appusr/var/etc/fileserver/def.png'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'db_emsg',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': '192.168.2.101',
            'PORT': '3306',
        }
    }

    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.2.100', '202.85.221.165', 'fileserver.lczybj.com']

ADMINS = ()
MANAGERS = ADMINS

TIME_ZONE = 'Asia/Chongqing'

LANGUAGE_CODE = 'en-us'

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


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

STATICFILES_DIRS = (
    op.join(op.dirname(op.dirname(__file__)), 'static'),
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

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



ROOT_URLCONF = 'fileserver.urls'

WSGI_APPLICATION = 'fileserver.wsgi.application'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'service',
    'fileserver',
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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/fileserver.log',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'service': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
