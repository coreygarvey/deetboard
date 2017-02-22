from salesengine.settings.base import *

INSTALLED_APPS += ('storages',)
AWS_STORAGE_BUCKET_NAME = "salesengine1"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL


DATABASES = {    
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST' : 'salesengine.cokkbzqljgtb.us-east-1.rds.amazonaws.com',
        'PORT' : '5432',
    }
}