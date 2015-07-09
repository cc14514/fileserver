#/usr/bin/env python
#coding=utf8
from __future__ import unicode_literals

from django.db import models


class FileserverCfg(models.Model):
    userid = models.CharField(max_length=64L)
    icon = models.CharField(max_length=300L,null=True, blank=True)
    appid = models.CharField(max_length=300L)
    appkey = models.CharField(max_length=200L)
    description = models.CharField(max_length=500L,null=True, blank=True)
    class Meta:
        verbose_name = '文件服务-Appid' 
        db_table = 'fileserver_cfg'
