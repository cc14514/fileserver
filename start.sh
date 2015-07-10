# python manage.py collectstatic
ps -ef |grep 9991|awk '{print $2}'|xargs kill -9
rm -rf fileserver/*.pyc
rm -rf service/*.pyc
uwsgi --processes 16 --threads 4 --buffer-size 32768 --http :9091 --socket :9991 --chdir `pwd` --module django_wsgi --stats /tmp/fileserver.socket &
