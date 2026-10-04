"""Prepara el alta de una empresa sin ejecutar SQL ni copiar datos existentes.

El SQL privado debe ejecutarlo un administrador PostgreSQL. Cada empresa usa
un rol LOGIN propietario sin privilegios globales.
"""
import argparse
import json
import os
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def private_write(path, content):
    with open(path, "x", encoding="utf-8", opener=lambda name, flags: os.open(name, flags, 0o600)) as handle:
        handle.write(content)


def prepare(company, name, port, directory, host="127.0.0.1", database_port=5432):
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", company) or company == "default":
        raise ValueError("Usa un identificador nuevo en minúsculas (default está reservado).")
    if not name.strip() or any(c in name for c in "\r\n\x00") or not 1024 <= port <= 65535:
        raise ValueError("Nombre o puerto inválido.")
    target = directory.resolve() / company
    target.mkdir(parents=True, mode=0o700)  # Nunca sobrescribe una empresa.
    database = "erp_" + company.replace("-", "_")
    role = database + "_app"
    password = secrets.token_urlsafe(36)
    data_root = ROOT / "tenant-data" / company
    profile = {
        "ERP_COMPANY_ID": company, "ERP_COMPANY_NAME": name,
        "ERP_DATA_ROOT": str(data_root), "ERP_SETTINGS_ENV": "dev",
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
        "POSTGRES_DB": database, "POSTGRES_USER": role, "POSTGRES_PASSWORD": password,
        "POSTGRES_HOST": host, "POSTGRES_PORT": str(database_port),
        "DJANGO_ALLOWED_HOSTS": "127.0.0.1,localhost", "ERP_AUTO_BACKUP_ENABLED": "false",
    }
    # JSON strings son compatibles con dotenv; ningún secreto va a stdout.
    private_write(target / "company.env", "\n".join(f"{key}={json.dumps(value, ensure_ascii=False)}" for key, value in profile.items()) + "\n")
    # Identificadores provienen exclusivamente de la validación anterior.
    sql = f'''\\set ON_ERROR_STOP on
CREATE ROLE "{role}" LOGIN PASSWORD '{password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE DATABASE "{database}" OWNER "{role}" TEMPLATE template0 ENCODING 'UTF8';
REVOKE ALL ON DATABASE "{database}" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE "{database}" TO "{role}";
\\connect {database}
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
'''
    private_write(target / "provision.sql", sql)
    private_write(target / "frontend-entry.json", json.dumps({"id": company, "name": name, "backend": f"http://127.0.0.1:{port}"}, indent=2) + "\n")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--directory", type=Path, default=ROOT / "config" / "companies")
    args = parser.parse_args()
    target = prepare(args.id, args.name, args.port, args.directory)
    print(f"Alta preparada en {target}. No se ha creado ni modificado ninguna base.")
    print("Ejecuta provision.sql con un administrador PostgreSQL; después usa company_manage.py para migrar y crear el usuario inicial.")


if __name__ == "__main__":
    main()
