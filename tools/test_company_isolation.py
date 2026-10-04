"""Verifica dos bases/roles, sesiones, datos y backups en PostgreSQL desechable."""
import os
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

from run_postgresql_tests import tool, ROOT, DJANGO_ROOT, PYTHON


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


def main():
    with tempfile.TemporaryDirectory(prefix="erp_isolation_") as temporary:
        root = Path(temporary); data = root / "pg"; sockets = root / "socket"; sockets.mkdir()
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
        run([tool("initdb"), "-D", str(data), "-A", "trust", "-U", "postgres", "--no-locale"])
        started = False
        try:
            run([tool("pg_ctl"), "-D", str(data), "-l", str(root / "postgres.log"), "-o", f"-F -p {port} -k {sockets}", "-w", "start"])
            started = True
            admin = [tool("psql"), "-h", str(sockets), "-p", str(port), "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1"]
            profiles = []
            for company in ("isolation_a", "isolation_b"):
                role = company + "_app"
                run(admin, input=f'CREATE ROLE {role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;\nCREATE DATABASE {company} OWNER {role};\nREVOKE ALL ON DATABASE {company} FROM PUBLIC;\n')
                env = os.environ.copy(); env.pop("ERP_ENV_FILE", None)
                env.update({"POSTGRES_DB": company, "POSTGRES_USER": role, "POSTGRES_PASSWORD": "test-only", "POSTGRES_HOST": str(sockets), "POSTGRES_PORT": str(port), "ERP_COMPANY_ID": company, "ERP_COMPANY_NAME": company, "ERP_DATA_ROOT": str(root / company), "DJANGO_SECRET_KEY": "test-key-" + company, "ERP_AUTO_BACKUP_ENABLED": "false", "DJANGO_ALLOWED_HOSTS": "testserver,localhost,127.0.0.1"})
                run([str(PYTHON), "manage.py", "migrate", "--noinput"], cwd=DJANGO_ROOT, env=env)
                profiles.append(env)
            shared = root / "session.txt"
            setup = '''from django.contrib.auth import get_user_model
from django.test import Client
from DATA_scope.models import PayrollPeriod
from pathlib import Path
import os
user=get_user_model().objects.create_user(username="same-user",password="Company-test-password-2026")
assert user.pk == 1
client=Client()
'''
            run([str(PYTHON), "manage.py", "shell", "-c", setup + f'''
PayrollPeriod.objects.create(periodo="202609",year=2026,month=9)
assert client.login(username="same-user",password="Company-test-password-2026")
Path({str(shared)!r}).write_text(client.cookies["sessionid"].value)
assert client.get("/api/v1/session/").json()["company"]["id"] == "isolation_a"
'''], cwd=DJANGO_ROOT, env=profiles[0])
            run([str(PYTHON), "manage.py", "shell", "-c", setup + f'''
assert PayrollPeriod.objects.count() == 0
client.cookies["sessionid"]=Path({str(shared)!r}).read_text()
assert client.get("/api/v1/session/").json()["authenticated"] is False
assert client.get("/api/v1/resources/periods/").status_code == 403
assert client.login(username="same-user",password="Company-test-password-2026")
assert client.get("/api/v1/session/").json()["company"]["id"] == "isolation_b"
'''], cwd=DJANGO_ROOT, env=profiles[1])
            for index, env in enumerate(profiles):
                other = profiles[1-index]["POSTGRES_DB"]
                result = subprocess.run([tool("psql"), "-h", str(sockets), "-p", str(port), "-U", env["POSTGRES_USER"], "-d", other, "-c", "SELECT 1"], capture_output=True, text=True)
                assert result.returncode != 0 and "permission denied" in result.stderr, "El rol pudo conectar a la otra empresa"
                run([str(PYTHON), "manage.py", "backup_database"], cwd=DJANGO_ROOT, env=env)
                backups = list((Path(env["ERP_DATA_ROOT"]) / "backups").glob("*.dump"))
                assert len(backups) == 1 and env["POSTGRES_DB"] in backups[0].name
                assert backups[0].stat().st_mode & 0o077 == 0
                assert not (Path(env["ERP_DATA_ROOT"]) / "uploads").exists()
            print("OK: dos bases y roles independientes; datos, sesiones y respaldos aislados; conexiones cruzadas denegadas.")
        except subprocess.CalledProcessError as exc:
            # Solo se ejecutan fixtures sintéticos; nunca credenciales reales.
            print(exc.stdout); print(exc.stderr)
            raise
        finally:
            if started:
                run([tool("pg_ctl"), "-D", str(data), "-m", "fast", "-w", "stop"])


if __name__ == "__main__":
    main()
