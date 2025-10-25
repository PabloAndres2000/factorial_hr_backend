# factorial_hr/settings/base.py
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',                     # Django REST Framework
    'rest_framework.authtoken',           # Token auth (si lo usas)
    'admin_interface',                    # Admin interface moderna
    'colorfield',                         # Soporte para colorfield en admin
    'simple_history',
]

APPLICATION_APPS = [
    "factorial_hr.apps.users",
    "factorial_hr.apps.auth",

]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + APPLICATION_APPS 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'factorial_hr.urls'

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

WSGI_APPLICATION = 'factorial_hr.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuración de proveedores OAuth
OAUTH_PROVIDERS = {
    'google': {
        'well_known_url': 'https://accounts.google.com/.well-known/openid-configuration',
        'audience': '407408718192.apps.googleusercontent.com',
        'display_name': 'Google',
        'enabled': True,
    },
    'microsoft': {
        'well_known_url': 'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
        'audience': 'your-microsoft-client-id',  # Reemplaza con tu Client ID de Microsoft
        'display_name': 'Microsoft Outlook',
        'enabled': True,
    },
    'github': {
        'well_known_url': 'https://token.actions.githubusercontent.com/.well-known/openid-configuration',
        'audience': 'your-github-client-id',  # Reemplaza con tu Client ID de GitHub
        'display_name': 'GitHub',
        'enabled': False,  # Deshabilitado por defecto
    }
}

# Configuración de autenticación
AUTH_REFRESH_TTL_DAYS = 7

# Configuración por defecto (para compatibilidad hacia atrás)
DEFAULT_OAUTH_PROVIDER = 'google'