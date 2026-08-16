from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DJANGO_ROOT = ROOT / "Celestial_ERP"
PYTHON = ROOT / "venv" / "bin" / "python"


def tool(name: str) -> str:
    direct = shutil.which(name)
    if direct:
        return direct
    candidates = sorted(Path("/usr/lib/postgresql").glob(f"*/bin/{name}"), reverse=True)
    if not candidates:
        raise RuntimeError(f"No se encontro {name}")
    return str(candidates[0])


def run(command: list[str], **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def main() -> int:
    cluster_root = Path(tempfile.mkdtemp(prefix="celestial_pg_tests_"))
    data_dir = cluster_root / "data"
    socket_dir = cluster_root / "socket"
    socket_dir.mkdir()
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    initdb = tool("initdb")
    pg_ctl = tool("pg_ctl")
    started = False
    try:
        run([initdb, "-D", str(data_dir), "-A", "trust", "-U", "postgres", "--no-locale"], capture_output=True)
        run([
            pg_ctl, "-D", str(data_dir), "-l", str(cluster_root / "postgres.log"),
            "-o", f"-F -p {port} -k {socket_dir}", "-w", "start",
        ], capture_output=True)
        started = True
        env = os.environ.copy()
        env.update({
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "postgres",
            # El cluster temporal usa autenticacion trust, pero settings exige
            # una credencial no vacia para evitar configuraciones inseguras.
            "POSTGRES_PASSWORD": "isolated-test-only",
            "POSTGRES_HOST": str(socket_dir),
            "POSTGRES_PORT": str(port),
            "ERP_AUTO_BACKUP_ENABLED": "false",
        })
        apps = sys.argv[1:] or [
            "Applet", "DATA_scope", "ERP_api", "Accounting", "Inventory", "Commerce", "Attendance",
        ]
        completed = subprocess.run(
            [str(PYTHON), "manage.py", "test", *apps],
            cwd=DJANGO_ROOT,
            env=env,
        )
        return completed.returncode
    finally:
        if started:
            subprocess.run([pg_ctl, "-D", str(data_dir), "-m", "fast", "-w", "stop"], capture_output=True)
        shutil.rmtree(cluster_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
