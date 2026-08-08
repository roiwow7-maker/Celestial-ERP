from __future__ import annotations

import os
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
ERP_SETTINGS_ENV = os.environ.get("ERP_SETTINGS_ENV", "dev").lower()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


def local_secret_key() -> str:
    secret_path = BASE_DIR / ".django_secret_key"
    if secret_path.exists():
        return secret_path.read_text(encoding="utf-8").strip()
    secret = "django-local-" + secrets.token_urlsafe(48)
    secret_path.write_text(secret, encoding="utf-8")
    return secret


def postgres_password() -> str:
    value = os.environ.get("POSTGRES_PASSWORD")
    if value:
        return value
    password_path = BASE_DIR / ".postgres_password"
    if password_path.exists():
        return password_path.read_text(encoding="utf-8").strip()
    return ""


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", local_secret_key())

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "Applet.apps.AppletConfig",
    "DATA_scope.apps.DataScopeConfig",
    "Attendance.apps.AttendanceConfig",
    "Accounting.apps.AccountingConfig",
    "Inventory.apps.InventoryConfig",
    "Commerce.apps.CommerceConfig",
    "ERP_api.apps.ErpApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "Applet.middleware.AutoBackupMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Celestial_ERP.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Applet" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "Applet.context_processors.erp_version",
            ],
        },
    },
]

WSGI_APPLICATION = "Celestial_ERP.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "celestial_erp"),
        # PostgreSQL normaliza a minusculas los roles creados sin comillas.
        "USER": os.environ.get("POSTGRES_USER", "admin_cerp"),
        "PASSWORD": postgres_password(),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": int(os.environ.get("POSTGRES_CONN_MAX_AGE", "60")),
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", str(PROJECT_ROOT / "staticfiles"))

SERVE_STATIC_LOCALLY = env_bool("DJANGO_SERVE_STATIC_LOCALLY", default=True)
# El mecanismo incluido actualmente usa la API nativa de SQLite. Se mantiene
# desactivado con PostgreSQL hasta disponer de respaldos basados en pg_dump.
AUTO_BACKUP_ENABLED = env_bool("ERP_AUTO_BACKUP_ENABLED", default=False)
AUTO_BACKUP_INTERVAL_MINUTES = int(os.environ.get("ERP_AUTO_BACKUP_INTERVAL_MINUTES", "90"))

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "applet:home"
LOGOUT_REDIRECT_URL = "login"

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "celestial_erp.log",
            "maxBytes": int(os.environ.get("ERP_LOG_MAX_BYTES", "5242880")),
            "backupCount": int(os.environ.get("ERP_LOG_BACKUP_COUNT", "5")),
            "encoding": "utf-8",
            "formatter": "standard",
        },
        "etl_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "etl.log",
            "maxBytes": int(os.environ.get("ERP_LOG_MAX_BYTES", "5242880")),
            "backupCount": int(os.environ.get("ERP_LOG_BACKUP_COUNT", "5")),
            "encoding": "utf-8",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "django.request": {
            "handlers": ["app_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "Applet": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "DATA_scope": {
            "handlers": ["console", "app_file", "etl_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "Attendance": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "ERP_api": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "Inventory": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "Commerce": {
            "handlers": ["console", "app_file"],
            "level": os.environ.get("ERP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
