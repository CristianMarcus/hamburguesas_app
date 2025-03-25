"""Configuración de Django para el proyecto HamburguesasApp."""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno desde .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-3)d$4189+p85!f856*p4s6gq$2y3635&46*y!9&4*!2t5j4r')

DEBUG = True


ALLOWED_HOSTS = ['hamburguesas-app.onrender.com', '127.0.0.1']  # Cambiar en producción

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Carpeta donde se recopilarán
#STATICFILES_DIRS = [
 #   os.path.join(BASE_DIR, 'static'),  # Asegúrate de que esta carpeta existe
#]



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Asegura que el directorio 'media/temp' exista
TEMP_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'temp')
os.makedirs(TEMP_MEDIA_ROOT, exist_ok=True)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pedidos.apps.PedidosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'pedidos': {  # Reemplaza 'pedidos' con el nombre de tu aplicación
            'handlers': ['console'],
            'level': 'DEBUG',  # Establece el nivel a DEBUG para ver todos los logs
        },
    },
}

ROOT_URLCONF = 'HamburguesasApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pedidos/templates')],
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

WSGI_APPLICATION = 'HamburguesasApp.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
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

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'