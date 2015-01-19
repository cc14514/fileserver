# python manage.py collectstatic
uwsgi --http :9091 --socket :9991 --chdir `pwd` --module django_wsgi
