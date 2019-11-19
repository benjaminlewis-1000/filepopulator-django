"""
Django settings for picasa project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from celery.schedules import crontab
import logging

# # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/2.2/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/')


LOCKFILE = os.path.join(PROJECT_ROOT, 'adding.lock')
if os.path.isfile(LOCKFILE):
    os.remove(LOCKFILE)

STATICFILES_DIRS = (
    os.path.join(STATIC_ROOT, 'admin'), 
    os.path.join(STATIC_ROOT, 'rest_framework'), 
    # os.path.join(STATIC_ROOT), 
)
# print(STATICFILES_DIRS)

from unipath import Path

# BASE_DIR         =  Path(__file__).ancestor(2)
# MEDIA_ROOT       =  BASE_DIR.child('media')
# STATIC_ROOT      =  BASE_DIR.child('static')

# TEMPLATE_DIRS    = (
#     BASE_DIR.child('templates'),
# )

# STATICFILES_DIRS = (
#     BASE_DIR.child('picasa').child('static'),
# )

STATIC_URL         = '/static/'
MEDIA_URL          = '/media/'
# print(STATICFILES_DIRS, STATIC_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '46r=!b*lkf2-^#a=40kq(9nxkfz53d7!ft7_iccd1!2aa%q@6z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'periodic.apps.PeriodicConfig',
    'rest_framework',
    'filepopulator',
    'face_manager',
    'api',
    # 'upload_img',
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

ROOT_URLCONF = 'picasa.urls'

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

WSGI_APPLICATION = 'picasa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DB_NAME = 'picasa'
DB_USER = 'benjamin'
DB_PASS = 'lewis'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True




# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/New_York'

CELERY_BEAT_SCHEDULE = {

#  'send-summary-every-hour': {
#        'task': 'summary',
#         # There are 4 ways we can handle time, read further 
#        'schedule': 3.0,
#         # If you're using any arguments
#        'args': ("We don’t need any",),
#     },
    # # Executes every Friday at 4pm
    # 'send-notification-on-friday-afternoon': { 
    #      'task': 'periodic.tasks.send_notification', 
    #  'schedule': crontab(minute=''),
    # },   
    # 'write-time-two-min': {
    #     'task': 'time_write',
    #     'schedule': 20.0, # crontab(minute='*/2'),
    # },
    'filepopulate_root': {
        'task': 'filepopulator.populate_files_from_root',
        'schedule': crontab(minute='*/1'),
    }

}

# FILEPOPULATOR settings


FILEPOPULATOR_THUMBNAIL_DIR = '/home/benjamin/git_repos/picasa_files/thumbnails' # place to store thumbnails that are derived from the images. 
# FILEPOPULATOR_THUMBNAIL_SIZE_TINY = (30, 30)
# FILEPOPULATOR_THUMBNAIL_SIZE = (250, 250)
FILEPOPULATOR_THUMBNAIL_SIZE_BIG = (500, 500)
FILEPOPULATOR_THUMBNAIL_SIZE_MEDIUM = (250, 250)
FILEPOPULATOR_THUMBNAIL_SIZE_SMALL = (100, 100)
FILEPOPULATOR_SERVER_IMG_DIR = '/home/benjamin/git_repos/picasa_files/actual_imgs' # root location of images you want to index into. (This maybe will change)
FILEPOPULATOR_CODE_DIR = '/home/benjamin/git_repos/local_picasa' # root directory of the code. 
FILEPOPULATOR_VAL_DIRECTORY = '/home/benjamin/git_repos/picasa_files/test_imgs'  # point to a directory that will have validation images when testing the app.
FILEPOPULATOR_MAX_SHORT_EDGE_THUMBNAIL =150 # Maximum size of the short edge for thumbnails.

LOG_LEVEL=logging.ERROR
LOG_FILE='test.log'


LOGGER = logging.getLogger(__name__)

LOGGER.setLevel(LOG_LEVEL) # or whatever
console = logging.StreamHandler()
file = logging.FileHandler(LOG_FILE)
#set a level on the handlers if you want;
#if you do, they will only output events that are >= that level
LOGGER.addHandler(console)
LOGGER.addHandler(file)