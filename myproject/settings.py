"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 3.2.23.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file

#retrieve DB variables
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')

qas_db_name = os.environ.get('QAS_DB_NAME')
qas_db_user = os.environ.get('QAS_DB_USER')
qas_db_password = os.environ.get('QAS_DB_PASSWORD')
qas_db_host = os.environ.get('QAS_DB_HOST')
financials_PRD_secret_key = os.environ.get('Secret_Key')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = financials_PRD_secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')
#print(DEBUG)
# Fetch the environment variable
#allowed_hosts_str = os.environ.get('Allowed_Hosts', '')

# Split the string by comma if it's not empty, otherwise default to an empty list
#ALLOWED_HOSTS = allowed_hosts_str.split(',') if allowed_hosts_str else []
ALLOWED_HOSTS = os.getenv('Allowed_Hosts', '').split(',')

#print(ALLOWED_HOSTS)
#ALLOWED_HOSTS = ['*']
# For debugging, print the ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'financials',
    'django_select2',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'
#gunicorn --bind 0.0.0.0:8000 

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qas_db',
        'USER': qas_db_user,
        'PASSWORD': qas_db_password,
        'HOST':  'localhost',
        'PORT': '5432',
    },
        'production': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST':  db_host,
        'PORT': '5432',
    }
}

# Set to True to use production database
USE_PRODUCTION_DB = os.environ.get('USE_PRODUCTION_DB') 

if USE_PRODUCTION_DB:
    DATABASES['default'] = DATABASES['production']

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/var/www/myproject/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
