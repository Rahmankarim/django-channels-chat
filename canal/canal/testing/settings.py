import os

from ..settings import *

"""
If you are using windows by default, the permissions to access subfolders for tests are disabled
Activate them using NOSE_INCLUDE_EXE = 1 or an environment variable in your OS with the same name and value
"""
os.environ['NOSE_INCLUDE_EXE'] = "1"
"""
Other settings
"""
DEBUG = True
TESTING = True

REUSE_DB = bool(int(os.environ.get("REUSE_DB", 0)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

if REUSE_DB:
    DATABASE_ROUTERS = []

# nosetests - NoseTestSuiteRunner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


# Args passed to nose
NOSE_ARGS = ['--with-coverage', '--cover-package=apps,lib,spectrum',
             "--logging-clear-handlers", "--logging-filter", "INFO"]

# We don't want to run Memcached for tests.
SESSION_ENGINE = "django.contrib.sessions.backends.db"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'api': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'staticfiles': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'depictions': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'thumbnails': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}
