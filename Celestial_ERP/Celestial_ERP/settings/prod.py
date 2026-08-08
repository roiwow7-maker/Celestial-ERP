from .base import *  # noqa: F401,F403


DEBUG = env_bool("DJANGO_DEBUG", default=False)  # noqa: F405

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)  # noqa: F405
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)  # noqa: F405

if not DEBUG and SECRET_KEY.startswith("django-local-"):  # noqa: F405
    raise RuntimeError("Define DJANGO_SECRET_KEY para ERP_SETTINGS_ENV=prod.")

