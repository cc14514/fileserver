#!/usr/bin/env bash
# python manage.py collectstatic

WORKERS=16
THREADS=10
LISTEN=2000

WSGI_HTTP_PORT=9091
WSGI_SOCKET_PORT=9991
WSGI_LOG_PATH=/home/appusr/var/log/fileserver.wsgi.log

ps -ef | grep $WSGI_SOCKET_PORT | awk '{print $2}' | xargs kill -9
rm -rf fileserver/*.pyc
rm -rf service/*.pyc
uwsgi -l $LISTEN --workers $WORKERS --threads $THREADS --buffer-size 32768 --http :$WSGI_HTTP_PORT --socket :$WSGI_SOCKET_PORT --chdir `pwd` --module fileserver.wsgi --stats /tmp/fileserver.socket -d $WSGI_LOG_PATH

echo SERVER STARTED.