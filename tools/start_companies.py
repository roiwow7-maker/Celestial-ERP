"""Inicia backends locales registrados; reutiliza los que ya están activos."""
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent


def main():
    registry = ROOT / "config" / "companies.json"
    companies = json.loads(registry.read_text()) if registry.exists() else [{"id": "default", "backend": "http://127.0.0.1:8000"}]
    children = []
    def stop(*_args):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        for company in companies:
            url = urlparse(company["backend"])
            if url.hostname != "127.0.0.1" or url.scheme != "http" or not url.port:
                raise RuntimeError("Este lanzador es solo para backends locales en 127.0.0.1.")
            try:
                with urlopen(company["backend"] + "/api/v1/session/", timeout=3) as response:
                    if response.headers.get("X-ERP-Company") != company["id"]:
                        raise RuntimeError("El puerto ya corresponde a otra empresa.")
                    print(f"Ya activo: {company['id']}", flush=True)
                    continue
            except URLError:
                pass
            if company["id"] == "default":
                command = [sys.executable, str(ROOT / "Celestial_ERP" / "manage.py")]
            else:
                profile = ROOT / "config" / "companies" / company["id"] / "company.env"
                command = [sys.executable, str(ROOT / "tools" / "company_manage.py"), "--profile", str(profile)]
            command += ["runserver", f"127.0.0.1:{url.port}", "--noreload"]
            children.append(subprocess.Popen(command, start_new_session=True))
        while children:
            if any(child.poll() is not None for child in children):
                raise RuntimeError("Un backend se detuvo. Revisa su salida antes de continuar.")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        import os
        for child in children:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait()


if __name__ == "__main__":
    main()
