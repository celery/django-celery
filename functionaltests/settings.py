import djcelery

INSTALLED_APPS = (
    'south',
    'djcelery',
    'kombu.transport.django',
    'django_nose',
    'someapp',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CELERY_TRACK_STARTED=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'functionaltest.sqlite3', 
        'TEST_NAME': 'testdb',
    }
}

BROKER_URL = 'django://'
