import os
from pathlib import (
    Path,
)

from dotenv import (
    load_dotenv,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    default="SUP3R-S3CR3T-K3Y-F0R-MY-PR0J3CT",
)

DEBUG = os.getenv(
    "DEBUG",
    default=False,
)

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    default="",
).split()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rest_framework.authtoken",
    "djoser",
    "users",
    "recipes",
    "api",
    "sorl.thumbnail",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES_DIR = BASE_DIR.parent / "docs"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv(
            "POSTGRES_DB",
            "django",
        ),
        "USER": os.getenv(
            "POSTGRES_USER",
            "django_user",
        ),
        "PASSWORD": os.getenv(
            "POSTGRES_PASSWORD",
            "",
        ),
        "HOST": os.getenv(
            "DB_HOST",
            "db",
        ),
        "PORT": os.getenv(
            "DB_PORT",
            5432,
        ),
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(
    BASE_DIR,
    "collected_static",
)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(
    BASE_DIR,
    "media",
)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination"
    ".PageNumberPagination",
    "PAGE_SIZE": 6,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USER": "True",
    "SERIALIZERS": {
        "user": "api.v1.serializers.UserSerializer",
	"current_user": "api.v1.serializers.UserSerializer",
    },
    "PERMISSIONS": {
        "user": ("rest_framework.permissions.IsAuthenticated"),
	'user_list': ['rest_framework.permissions.AllowAny'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        "user_delete": ("rest_framework.permissions.IsAdminUser"),
    },
}

AUTH_USER_MODEL = "users.User"

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(
    BASE_DIR,
    "sent_emails",
)
DEFAULT_FROM_EMAIL = "admin@example.com"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
