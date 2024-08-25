"""
Django settings for radis project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from pathlib import Path

import environ
import toml

env = environ.Env()

# The base directory of the project (the root of the repository)
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Used to monitor for autoreload
SOURCE_FOLDERS = [BASE_DIR / "radis"]

# Read pyproject.toml to fetch current version. We do this conditionally as the
# RADIS client library uses RADIS for integration tests installed as a package
# (where no pyproject.toml is available).
if (BASE_DIR / "pyproject.toml").exists():
    pyproject = toml.load(BASE_DIR / "pyproject.toml")
    PROJECT_VERSION = pyproject["tool"]["poetry"]["version"]
else:
    PROJECT_VERSION = "???"

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)  # type: ignore
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# Our custom site settings that are also available in the templates,
# see adit-radis-shared/common/site.py#base_context_processor
SITE_BASE_URL = env.str("SITE_BASE_URL", default="http://localhost:8000")  # type: ignore
SITE_DOMAIN = env.str("SITE_DOMAIN", default="localhost")  # type: ignore
SITE_NAME = env.str("SITE_NAME", default="ADIT")  # type: ignore
SITE_META_KEYWORDS = "RADIS,Radiology,Reports,Medicine,Tool"
SITE_META_DESCRIPTION = "RADIS is an application to archive, query and collect radiology reports"
SITE_PROJECT_URL = "https://github.com/openradx/radis"

INSTALLED_APPS = [
    "daphne",
    "whitenoise.runserver_nostatic",
    "adit_radis_shared.common.apps.CommonConfig",
    "registration",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "django_extensions",
    "procrastinate.contrib.django",
    "dbbackup",
    "revproxy",
    "loginas",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_htmx",
    "django_tables2",
    "formtools",
    "rest_framework",
    "adrf",
    "radis.core.apps.CoreConfig",
    "adit_radis_shared.accounts.apps.AccountsConfig",
    "adit_radis_shared.token_authentication.apps.TokenAuthenticationConfig",
    "radis.reports.apps.ReportsConfig",
    "radis.search.apps.SearchConfig",
    "radis.rag.apps.RagConfig",
    "radis.subscriptions.apps.SubscriptionsConfig",
    "radis.collections.apps.CollectionsConfig",
    "radis.notes.apps.NotesConfig",
    "radis.pgsearch.apps.PgSearchConfig",
    "channels",
    "betterforms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "adit_radis_shared.accounts.middlewares.ActiveGroupMiddleware",
    "adit_radis_shared.common.middlewares.MaintenanceMiddleware",
    "adit_radis_shared.common.middlewares.TimezoneMiddleware",
]

ROOT_URLCONF = "radis.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "adit_radis_shared.common.site.base_context_processor",
                "radis.reports.site.base_context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "radis.wsgi.application"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# env.db() loads the DB setup from the DATABASE_URL environment variable using
# Django-environ.
# The sqlite database is still used for pytest tests.
DATABASES = {"default": env.db(default="sqlite:///radis-sqlite.db")}  # type: ignore

# Django 3.2 switched to BigAutoField for primary keys. It must be set explicitly
# and requires a migration.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# A custom authentication backend that supports a single currently active group.
AUTHENTICATION_BACKENDS = ["adit_radis_shared.accounts.backends.ActiveGroupModelBackend"]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# See following examples:
# https://github.com/django/django/blob/master/django/utils/log.py
# https://cheat.readthedocs.io/en/latest/django/logging.html
# https://stackoverflow.com/a/7045981/166229
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(name)-12s %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %Z",
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %Z",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "CRITICAL",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "radis": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "ERROR"},
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "de-de"

# We don't want to have German translations, but everything in English
USE_I18N = False

USE_TZ = True

TIME_ZONE = "UTC"

# All REST API requests must come from authenticated clients
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "adit_radis_shared.token_authentication.auth.RestTokenAuthentication",
    ],
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_DIRS = (BASE_DIR / "radis" / "static",)

STATIC_URL = "/static/"

STATIC_ROOT = env.str("DJANGO_STATIC_ROOT", default=(BASE_DIR / "staticfiles"))  # type: ignore

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Where to redirect to after login
LOGIN_REDIRECT_URL = "home"

# django-dbbackup
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {
    "location": env.str("BACKUP_DIR", default=(BASE_DIR / "backups")),  # type: ignore
}
DBBACKUP_CLEANUP_KEEP = 30

# For crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# django-templates2
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5.html"

# This seems to be important for development on Gitpod as CookieStorage
# and FallbackStorage does not work there.
# Seems to be the same problem with Cloud9 https://stackoverflow.com/a/34828308/166229
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

EMAIL_SUBJECT_PREFIX = "[RADIS] "

# An Email address used by the RADIS server to notify about finished jobs and
# management notifications.
SERVER_EMAIL = env.str("DJANGO_SERVER_EMAIL", default="support@radis.test")  # type: ignore
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# A support Email address that is presented to the users where
# they can get support.
SUPPORT_EMAIL = env.str("SUPPORT_EMAIL", default=SERVER_EMAIL)  # type: ignore

# Also used by django-registration-redux to send account approval emails
admin_first_name = env.str("ADMIN_FIRST_NAME", default="RADIS")  # type: ignore
admin_last_name = env.str("ADMIN_LAST_NAME", default="Admin")  # type: ignore
admin_full_name = admin_first_name + " " + admin_last_name
ADMINS = [
    (
        admin_full_name,
        env.str("ADMIN_EMAIL", default="admin@radis.test"),  # type: ignore
    )
]

# Settings for django-registration-redux
REGISTRATION_FORM = "adit_radis_shared.accounts.forms.RegistrationForm"
ACCOUNT_ACTIVATION_DAYS = 14
REGISTRATION_OPEN = True

# Channels
ASGI_APPLICATION = "radis.asgi.application"

# Used by django-filter
FILTERS_EMPTY_CHOICE_LABEL = "Show All"

# A timezone that is used for users of the web interface.
USER_TIME_ZONE = env.str("USER_TIME_ZONE", default="Europe/Berlin")  # type: ignore

# The salt that is used for hashing new tokens in the token authentication app.
# Cave, changing the salt after some tokens were already generated makes them all invalid!
TOKEN_AUTHENTICATION_SALT = env.str(
    "TOKEN_AUTHENTICATION_SALT",
    default="Rn4YNfgAar5dYbPu",  # type: ignore
)

# Language specific setup. Currently only German and English are supported.
SUPPORTED_LANGUAGES = ["de", "en"]

# llama.cpp
LLAMACPP_URL = env.str("LLAMACPP_URL", default="http://localhost:8088")  # type: ignore

# Chat settings
CHAT_SYSTEM_PROMPT = {
    "de": "Du bist ein radiologischer Facharzt",
    "en": "You are a radiologist",
}
CHAT_ANSWER_YES = {
    "de": "Ja",
    "en": "Yes",
}
CHAT_ANSWER_NO = {
    "de": "Nein",
    "en": "No",
}
CHAT_USER_PROMPT = {
    "de": f"""
        Im folgenden erhälst Du einen radiologischen Befund und eine Frage zu diesem Befund.
        Beantworte die Frage zu dem Befund mit {CHAT_ANSWER_YES['de']} oder {CHAT_ANSWER_NO['de']}.
        Befund: $report
        Frage: $question
        Antwort: 
    """,
    "en": f"""
        In the following you will find a radiological report and a question about this report.
        Answer the question about the report with {CHAT_ANSWER_YES['en']} or {CHAT_ANSWER_NO['en']}.
        Report: $report
        Question: $question
        Answer:
    """,
}

# RAG
RAG_DEFAULT_PRIORITY = 2
RAG_URGENT_PRIORITY = 3

# The number of RAG report instances that are processed within one task. There are multiple
# questions associated with each report instance via the RagJob.
RAG_TASK_BATCH_SIZE = 64
# The number of parallel requests the LLM can handle. This limit is enforced within each task. When
# having multiple workers, the total number of parallel requests is
# RAG_LLM_CONCURRENCY_LIMIT * number of workers. Either the number of HTTP Threads and number of
# parallel computing slots of the llama.cpp should be set to match this number or the continuous
# batching capability of the LLM or a combination of both should be used.
RAG_LLM_CONCURRENCY_LIMIT = 6

START_RAG_JOB_UNVERIFIED = False


# Subscription
SUBSCRIPTION_DEFAULT_PRIORITY = 3
SUBSCRIPTION_URGENT_PRIORITY = 4
SUBSCRIPTION_CRON = "* * * * *"
SUBSCRIPTION_REFRESH_TASK_BATCH_SIZE = 64
