# python manage.py collectstatic
ps -ef |grep 9991|awk '{print $2}'|xargs kill -9
rm -rf fileserver/*.pyc
rm -rf service/*.pyc

WORKERS=16
THREADS=10
LISTEN=2000

uwsgi -l $LISTEN --workers $WORKERS --threads $THREADS --buffer-size 32768 --http :9091 --socket :9991 --chdir `pwd` --module django_wsgi --stats /tmp/fileserver.socket -d /home/appusr/var/log/fileserver.wsgi.log

echo SERVER STARTED.