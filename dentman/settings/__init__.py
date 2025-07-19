import logging
import os
from pathlib import Path

import environ
from django.urls import reverse_lazy




class SpecialLogFilter(logging.Filter):
    def filter(self, record, *args, **kwargs):
        print("sp1", args)
        print("sp2", kwargs)
        print("sp3", vars(record))
        return True

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
ENV_FILE = str(ROOT_DIR / ".env")
APPS_DIR = ROOT_DIR / "app"

class DotEnv(environ.Env):
    def __getattr__(self, name):
        val = os.getenv(name)
        if val is None:
            raise SystemError(f"Variable {name} not defined in {ENV_FILE}")
        return val

env = DotEnv()
env.read_env(ENV_FILE)


ENV = env.ENV

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="Environment variables not defined!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

CSRF_TRUSTED_ORIGINS = ['https://dentman.pl']

# Ensure this is set if behind a proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Optionally, specify allowed hosts
ALLOWED_HOSTS = ['dentman.pl']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'formtools',

    'dentman.app',
    'dentman.ops',
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


ROOT_URLCONF = 'dentman.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ ROOT_DIR / 'templates' ],
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


WSGI_APPLICATION = 'dentman.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'app.User'

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 's/'
STATIC_ROOT = ROOT_DIR / 'pub/s/'
STATICFILES_DIRS = [ROOT_DIR / "static"]

MEDIA_URL = 'm/'
MEDIA_ROOT = ROOT_DIR / 'pub/m/'

STORAGE_URL = '/storage/'
STORAGE_ROOT = ROOT_DIR / 'storage/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'asyncio': {
            'level': 'WARNING', # avoid: "Using selector: EpollSelector"
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

