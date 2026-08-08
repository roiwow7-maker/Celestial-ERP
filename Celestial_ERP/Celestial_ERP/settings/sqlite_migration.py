"""Configuracion auxiliar para exportar la base SQLite historica.

No debe utilizarse para ejecutar la aplicacion. La configuracion normal usa
PostgreSQL desde ``base.py``.
"""

from .base import *  # noqa: F401,F403


DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        "OPTIONS": {
            "timeout": 20,
            "init_command": "PRAGMA foreign_keys=ON;",
        },
    }
}

AUTO_BACKUP_ENABLED = False
