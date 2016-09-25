# Django settings for testproj project.

import os
import sys
import warnings
warnings.filterwarnings(
    'error', r'DateTimeField received a naive datetime',
    RuntimeWarning, r'django\.db\.models\.fields')

# import source code dir
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.join(here, os.pardir))

import djcelery  # noqa
djcelery.setup_loader()

NO_NOSE = os.environ.get('DJCELERY_NO_NOSE', False)

SITE_ID = 300

DEBUG = True

ROOT_URLCONF = 'tests.urls'
SECRET_KEY = 'skskqlqlaskdsd'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

AUTOCOMMIT = True

if not NO_NOSE:
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

COVERAGE_EXCLUDE_MODULES = (
    'djcelery',
    'djcelery.tests.*',
    'djcelery.management.*',
    'djcelery.contrib.*',
)

NOSE_ARGS = [
    os.path.join(here, os.pardir, 'djcelery', 'tests'),
    os.environ.get('NOSE_VERBOSE') and '--verbose' or '',
    '--cover3-package=djcelery',
    '--cover3-branch',
    '--cover3-exclude=%s' % ','.join(COVERAGE_EXCLUDE_MODULES),
]

BROKER_URL = 'amqp://'

TT_HOST = 'localhost'
TT_PORT = 1978

CELERY_DEFAULT_EXCHANGE = 'testcelery'
CELERY_DEFAULT_ROUTING_KEY = 'testcelery'
CELERY_DEFAULT_QUEUE = 'testcelery'

CELERY_QUEUES = {'testcelery': {'binding_key': 'testcelery'}}

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'djcelery-test-db',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'dummy': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djcelery',
    'someapp',
    'someappwotask',
)

if not NO_NOSE:
    INSTALLED_APPS = INSTALLED_APPS + ('django_nose', )

CELERY_SEND_TASK_ERROR_EMAILS = False

USE_TZ = True
TIME_ZONE = 'UTC'
MIDDLEWARE = MIDDLEWARE_CLASSES = []
