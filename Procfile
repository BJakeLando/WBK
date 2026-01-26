release: python manage.py collectstatic --noinput && python manage.py migrate && python setup_admin.py
web: gunicorn mysite.wsgi:application