DEBUG = False
SECRET_KEY = """STRING_TO_CHANGE_1"""
CALDAV_PASSWORD = """STRING_TO_CHANGE_2"""
ALLOWED_HOSTS = ["STRING_TO_CHANGE_3"]
CSRF_TRUSTED_ORIGINS = ["STRING_TO_CHANGE_4"]
API_SECRET_KEY = """STRING_TO_CHANGE_5"""
CALDAV_URL = "http://127.0.0.1:5232"

STATIC_ROOT = "/opt/data/static"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/data/rtucaldav.sqlite3',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}