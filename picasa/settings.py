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
from datetime import timedelta, datetime
import random
import string

today = datetime.today()
random_seed = today.year * 10000 + today.month * 100 + today.day
random.seed(random_seed)

# # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/2.2/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if 'IN_DOCKER' in os.environ.keys():
    in_docker = True
else:
    in_docker = False

production = False
if 'PRODUCTION' in os.environ.keys():
    if os.environ['PRODUCTION'] == 'True':
        production = True

if in_docker:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PWD']
    DEV = os.environ['DEV'] == 'True'
    MEDIA_ROOT = '/media' # os.environ['MEDIA_FILES_LOCATION']
    if DEV:
        REDIS_HOST = 'task_redis_dev'
        DB_HOST = 'db_picasa_dev'
    else:
        REDIS_HOST = 'task_redis'
        DB_HOST = 'db_django'
        
    PHOTO_ROOT = '/photos'
    TEST_IMG_DIR_FILEPOPULATE = '/test_imgs_filepopulate'
#    ALLOWED_HOSTS = ['localhost', '127.0.0.1', os.environ['WEBAPP_DOMAIN']]
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', os.environ['DOMAINNAME'], os.environ['WEBAPP_DOMAIN'], 'flower.' + os.environ['DOMAINNAME']]
#    ALLOWED_HOSTS = ['localhost', '127.0.0.1', os.environ['DOMAINNAME'], os.environ['WEBAPP_DOMAIN'] ]
#    STATIC_URL = 'http://localhost/static/'
#    MEDIA_URL  = 'http://localhost:8080/'
    STATIC_URL = 'https://' + os.environ['MEDIA_DOMAIN'] + '/static/'
    MEDIA_URL = 'https://' + os.environ['MEDIA_DOMAIN'] + '/media/'
    LOG_DIR = '/var/log/picasa'
    STATIC_ROOT = os.environ['STATIC_LOCATION']
    MEDIA_URL_USER = os.environ['APACHE_USER']
    MEDIA_URL_PW = os.environ['APACHE_PWD']
else:
    DB_NAME = 'picasa'
    DB_USER = 'benjamin'
    DB_PASS = 'lewis'
    DB_HOST = 'localhost'
    REDIS_HOST = 'localhost'
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
    SECRET_KEY = '46r=!b*lkf2-^#a=40kq(9nxkfz53d7!ft7_iccd1!2aa%q@6z'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    PHOTO_ROOT = '/home/benjamin/git_repos/picasa_files/actual_imgs'
    TEST_IMG_DIR_FILEPOPULATE = '/home/benjamin/git_repos/picasa_files/test_imgs'

    STATIC_URL = 'http://localhost/static/'
    MEDIA_URL  = 'http://localhost/media/'
    STATIC_SERVER = '/var/www/html/static'
    LOG_DIR = '/home/benjamin/git_repos/picasa_files/logs'

RANDOM_ACCESS_KEY = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
print(MEDIA_URL)

# Set up logging
formatter = logging.Formatter('%(levelname)s | %(asctime)s - %(message)s')
LOGGER = logging.getLogger("__main__")
LOGGER.setLevel(logging.DEBUG)
LOGGER.propagate = False

fh_low = logging.FileHandler(os.path.join(LOG_DIR, 'picasa_debug.log'), 'a')
fh_low.setLevel(logging.DEBUG)
fh_low.setFormatter(formatter)
LOGGER.addHandler(fh_low)

fh_high = logging.FileHandler(os.path.join(LOG_DIR, 'picasa_important.log'), 'a')
fh_high.setLevel(logging.WARNING)
fh_high.setFormatter(formatter)
LOGGER.addHandler(fh_high)

fh_mid = logging.FileHandler(os.path.join(LOG_DIR, 'picasa_lite_debug.log'), 'a')
fh_mid.setLevel(logging.INFO)
fh_mid.setFormatter(formatter)
LOGGER.addHandler(fh_mid)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)
LOGGER.addHandler(ch)

if in_docker:
    LOGGER.warning("Allowed hosts is wrong in docker")

LOGGER.debug(f"Are we in production? {production}")

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

LOCKFILE = '/locks/adding.lock' # path.join(PROJECT_ROOT, 'adding.lock')
FACE_LOCKFILE = '/locks/face_add.lock'
CLASSIFY_LOCKFILE = '/locks/classify.lock'
# if os.path.isfile(LOCKFILE):
#     os.remove(LOCKFILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # True # not production # False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'periodic.apps.PeriodicConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'filepopulator',
    'face_manager',
    'api',
    'filters',
    'frontend',
    # 'webpack_loader',
    # 'upload_img',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#######################
# Webpack Configuration 
#######################
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'frontend', 'static'),
# )

# WEBPACK_LOADER = {
#     'DEFAULT' : {
#     ##TOCHANGE
#         # 'dist' is the location of webpack generated files.
#         'BUNDLE_DIR_NAME': 'dist/',
#         'STATS_FILE': os.path.join(BASE_DIR, 'frontend',  'webpack-stats.json')
#     }
# }
#######################
# /Webpack Configuration 
#######################

# CORS_ORIGIN_WHITELIST = [
#     "https://192.168.1.15:8080",
#     "https://192.168.1.145:8080",
#     "https://facewire.exploretheworld.tech",
#     "jsfiddle.net",
# ]

# CORS_ORIGIN_WHITELIST = (
#     "http://192.168.1.15:8080"
# )

# CORS_ORIGIN_REGEX_WHITELIST = [
#     r"*jsfiddle\.net*",
# ]

# Get the Django Rest Framework to use https in pagination links
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ORIGIN_ALLOW_ALL=True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

LOGGER.critical("CORS allowing from all...")

ROOT_URLCONF = 'picasa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(THIS_DIR, 'html')],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
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

# Token authentication: https://simpleisbetterthancomplex.com/tutorial/2018/11/22/how-to-implement-token-authentication-using-django-rest-framework.html
REST_FRAMEWORK = {
     'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100, 
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# JSON Web Tokens config
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'
LOGGER.debug(f"Time zone is {TIME_ZONE}")

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CELERY STUFF
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


# if production: 
CELERY_BEAT_SCHEDULE = {
    'filepopulate_root': {
        'task': 'filepopulator.populate_files_from_root',
        'schedule': crontab(minute='*/10') # , hour='*/6'),
        # 'schedule': crontab(minute='*/10'),
    },
    'dirs_datetimes': {
        'task': 'filepopulator.update_dir_dates',
        'schedule': crontab(minute=0, hour='*/12')
    },
    'face_add': {
        'task': 'face_manager.face_extraction', 
        'schedule': crontab( minute = '*/1'),
        # 'schedule': crontab( minute = '0', hour='*/2'),
        'options': {
            'expires': 30,
            # 'expires': 1800,
        }
    },
    'classify_unlabeled': {
        'task': 'face_manager.classify_unlabeled',
        'schedule': crontab(day_of_month = '*/5', minute=0, hour=0)
        # 'schedule': crontab(minute='*/2')
    }

}

# else:
#     CELERY_BEAT_SCHEDULE = {
    
#         'filepopulate_root': {
#             'task': 'filepopulator.populate_files_from_root',
#             'schedule': crontab(minute='*/1'),
#         },
#         'dirs_datetimes': {
#             'task': 'filepopulator.update_dir_dates',
#             'schedule': crontab(minute='*/1')
#         },
#         'face_add': {
#             'task': 'face_manager.face_extraction', 
#             'schedule': crontab( minute = '*/1'),
#             # 'schedule': crontab( minute = '0', hour='*/2'),
#             'options': {
#                 'expires': 30,
#                 # 'expires': 1800,
#             }
#         }

#     }

if not 'filepopulate_root' in CELERY_BEAT_SCHEDULE.keys():
    LOGGER.error("Filepopulate celery task not instantiated.")
    raise ValueError('Filepopulate celery task not instantiated.')
if not 'dirs_datetimes' in CELERY_BEAT_SCHEDULE.keys():
    LOGGER.error("Dirs_datetimes celery task not instantiated.")
    raise ValueError('Dirs_datetimes celery task not instantiated.')

# FILEPOPULATOR settings


# FILEPOPULATOR_THUMBNAIL_DIR = '/home/benjamin/git_repos/picasa_files/thumbnails' # place to store thumbnails that are derived from the images. 
# FILEPOPULATOR_THUMBNAIL_SIZE_TINY = (30, 30)
# FILEPOPULATOR_THUMBNAIL_SIZE = (250, 250)
FILEPOPULATOR_THUMBNAIL_SIZE_BIG = (500, 500)
FILEPOPULATOR_THUMBNAIL_SIZE_MEDIUM = (250, 250)
FILEPOPULATOR_THUMBNAIL_SIZE_SMALL = (100, 100)
FILEPOPULATOR_SERVER_IMG_DIR = PHOTO_ROOT # root location of images you want to index into. (This maybe will change)
FILEPOPULATOR_CODE_DIR = PROJECT_ROOT # '/home/benjamin/git_repos/local_picasa' # root directory of the code. 
FILEPOPULATOR_VAL_DIRECTORY = TEST_IMG_DIR_FILEPOPULATE  # point to a directory that will have validation images when testing the app.
FILEPOPULATOR_MAX_SHORT_EDGE_THUMBNAIL =150 # Maximum size of the short edge for thumbnails.

FACE_THUMBNAIL_SIZE=(200, 200)

# logging.error("TODO: Set up apache server. STATIC_URL needs to be served by it.")

BLANK_FACE_NAME='_NO_FACE_ASSIGNED_'
BLANK_FACE_IMG_PATH=os.path.join(SITE_ROOT, 'blank_person.png')

# Parameters for the machine learning model
if DEV:
    FACE_NUM_THRESH = 1
else:
    FACE_NUM_THRESH=50
IGNORED_NAMES=[BLANK_FACE_NAME, '.ignore', '.realignore', '.jessicatodo', '.cutler_tbd']
