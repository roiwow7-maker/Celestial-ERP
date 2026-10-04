"""Ejecuta comandos Django con un perfil explícito e independiente de empresa."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    profile = args.profile.resolve()
    if not profile.is_file() or not args.command:
        parser.error("Indica un perfil existente y un comando Django.")
    values = dotenv_values(profile)
    required = {"ERP_COMPANY_ID", "ERP_DATA_ROOT", "DJANGO_SECRET_KEY", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT"}
    if any(not values.get(key) for key in required):
        parser.error("El perfil está incompleto. No se permite heredar credenciales de otra empresa.")
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("POSTGRES_", "DJANGO_", "ERP_")):
            del env[key]
    env.update({key: value for key, value in values.items() if value is not None})
    env["ERP_ENV_FILE"] = str(profile)
    return subprocess.call([sys.executable, "manage.py", *args.command], cwd=ROOT / "Celestial_ERP", env=env)


if __name__ == "__main__":
    raise SystemExit(main())
