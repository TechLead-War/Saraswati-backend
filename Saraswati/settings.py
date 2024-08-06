import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-(4o&&4q*h#f6#ryzzy7^!p3c3j^-xb7j2p(%_8s-+=64gai&gw"
DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'exam',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'corsheaders',
]

CORS_ALLOWED_ORIGINS = [
    'http://192.168.1.3:3000',
    'http://localhost:3000',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'Saraswati.middleware.SetSearchPathMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'Saraswati.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'Saraswati.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("SERVICE_DATABASE_NAME"),
        "USER": os.getenv("SERVICE_DATABASE_USERNAME"),
        "PASSWORD": os.getenv("SERVICE_DATABASE_PASSWORD"),
        "HOST": os.getenv("SERVICE_DATABASE_HOST"),
        "PORT": os.getenv("SERVICE_DATABASE_PORT"),
    }
}


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

LANGUAGE_CODE = 'en-us'
USE_I18N = True
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
