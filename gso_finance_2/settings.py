"""
Django settings for gso_finance_2 project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1-5awwa(vby89vmf_xra6+@5_)oml==&2yrf(!60+i(b92&nbz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['vegeto', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'common',
    'eamcom',
    'portfolio',
    'security',
    'providers',
    'rest_framework',
    'corsheaders',
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    'origin', 'cache-control'
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authentication.utility.AuthenticationMiddlewareJWT'
]

#REST_FRAMEWORK = {
#    'DEFAULT_PERMISSION_CLASSES': (
#        'rest_framework.permissions.AllowAny',
#    ),
#}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES' : ('rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ROOT_URLCONF = 'gso_finance_2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['D:/DEV/Sources/gso_finance_2/resources/templates'],
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

WSGI_APPLICATION = 'gso_finance_2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'amx_eamcom',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'gso_finance',
        'PASSWORD': 'boudux',
        'HOST': '127.0.0.1',
        'PORT': 5432                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


# URL prefix for static files.
STATIC_URL = '/statics/'

# Additional locations of static files
STATICFILES_DIRS = (
    'D:/DEV/Sources/gso_finance_2/resources/statics/',
)

RESOURCES_DIR = 'D:/DEV/Sources/gso_finance_2/resources/other'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gso_finance_2': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'pika': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'common': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
                
        'corsheaders': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'eamcom': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'portfolio': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'security': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'providers': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },

    }
}