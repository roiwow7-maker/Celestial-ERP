import os


environment = os.environ.get("ERP_SETTINGS_ENV", "dev").lower()

if environment == "prod":
    from .prod import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
