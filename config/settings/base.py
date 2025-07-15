import secrets
from pathlib import Path

from utils.env_config import get_env


env = get_env()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env.get_str(var_name="DJANGO_DEBUG", default="False", required=False).lower() in (
    "true",
    "1",
    "yes",
)

TEST = env.get_str(var_name="DJANGO_TEST", default="False", required=False).lower() in (
    "true",
    "1",
    "yes",
)

if TEST:
    SECRET_KEY = "".join(
        secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)
    )
else:
    SECRET_KEY = env.get_str(var_name="DJANGO_SECRET_KEY", required=True)

ALLOWED_HOSTS = env.get_list("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", required=True)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rest_framework_json_api",
    "drf_spectacular",
    "apps.account",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "rest_framework_json_api.exceptions.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework_json_api.pagination.JsonApiPageNumberPagination",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
        "rest_framework_json_api.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        "rest_framework_json_api.django_filters.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",
    "TEST_REQUEST_RENDERER_CLASSES": ("rest_framework_json_api.renderers.JSONRenderer",),
    "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


if not TEST:
    DATABASES = {
        "default": {
            "ENGINE": env.get_str("DB_ENGINE", default="django.db.backends.postgresql"),
            "NAME": env.get_str("DB_NAME"),
            "USER": env.get_str("DB_USER"),
            "PASSWORD": env.get_str("DB_PASSWORD"),
            "HOST": env.get_str("DB_HOST", default="localhost"),
            "PORT": env.get_int("DB_PORT", default=5432),
        }
    }

    REDIS_HOST = env.get_str("REDIS_HOST", default="redis")
    REDIS_PORT = env.get_int("REDIS_PORT", default=6379)
    REDIS_DB = env.get_int("REDIS_DB", default=1)
    REDIS_PASSWORD = env.get_str("REDIS_PASSWORD", default="", required=False)

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


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

SPECTACULAR_SETTINGS = {
    "TITLE": "Account API",
    "DESCRIPTION": "Account API",
    "VERSION": "v1",
    "SERVERS": [{"url": "/api/v1"}],
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SCHEMA_PATH_PREFIX_TRIM": True,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} [{name}:{lineno}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "INFO",
        },
        "console_errors": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "ERROR",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console_errors"],
            "level": "ERROR",
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
