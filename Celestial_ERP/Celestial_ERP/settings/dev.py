from .base import *  # noqa: F401,F403


DEBUG = env_bool("DJANGO_DEBUG", default=True)  # noqa: F405

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", default=False)  # noqa: F405
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", default=False)  # noqa: F405

