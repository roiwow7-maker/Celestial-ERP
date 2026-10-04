"""Publica una empresa en el selector solamente si su backend confirma su identidad."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=ROOT / "config" / "companies.json")
    args = parser.parse_args()
    company = json.loads(args.entry.read_text())
    with urlopen(company["backend"] + "/api/v1/session/", timeout=10) as result:
        payload = json.load(result)
        if result.headers.get("X-ERP-Company") != company["id"] or payload.get("company", {}).get("id") != company["id"]:
            raise SystemExit("Identidad de empresa incorrecta. Registro cancelado.")
    companies = json.loads(args.registry.read_text()) if args.registry.exists() else [{"id": "default", "name": "Empresa actual", "backend": "http://127.0.0.1:8000"}]
    if any(row["id"] == company["id"] or row["backend"] == company["backend"] for row in companies):
        raise SystemExit("El identificador o backend ya está registrado.")
    companies.append(company)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=args.registry.parent, delete=False) as handle:
        json.dump(companies, handle, ensure_ascii=False, indent=2)
        name = handle.name
    os.replace(name, args.registry)
    print(f"Empresa registrada: {company['name']}")


if __name__ == "__main__":
    main()
