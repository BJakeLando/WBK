release: python manage.py collectstatic --noinput && python manage.py migrate && python create_superuser.py
web: gunicorn mysite.wsgi:application
