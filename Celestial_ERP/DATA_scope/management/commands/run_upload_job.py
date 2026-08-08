from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from DATA_scope.quality import validate_transformed_csv, write_quality_report


def write_status(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class Command(BaseCommand):
    help = "Ejecuta una carga ETL web en segundo plano y actualiza su estado en uploads."

    def add_arguments(self, parser):
        parser.add_argument("job_config", type=Path)

    def handle(self, *args, **options):
        config_path: Path = options["job_config"]
        if not config_path.exists():
            raise CommandError(f"No existe job_config: {config_path}")

        config = json.loads(config_path.read_text(encoding="utf-8"))
        upload_dir = Path(config["upload_dir"])
        status_path = upload_dir / "job_status.json"
        stdout_path = upload_dir / "stdout.log"
        stderr_path = upload_dir / "stderr.log"

        status = {
            "run_id": config["run_id"],
            "status": "running",
            "input_name": config["input_name"],
            "return_code": None,
            "quality_issue_count": 0,
            "downloads": [],
            "error": "",
        }
        write_status(status_path, status)

        try:
            with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
                completed = subprocess.run(
                    config["command"],
                    cwd=config["project_root"],
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                    timeout=int(config.get("timeout_seconds", 1800)),
                )
            status["return_code"] = completed.returncode
            status["status"] = "success" if completed.returncode == 0 else "failed"
        except subprocess.TimeoutExpired:
            status["return_code"] = 124
            status["status"] = "failed"
            status["error"] = "La carga supero el tiempo maximo configurado."
            stderr_path.write_text(status["error"], encoding="utf-8")
        except Exception as exc:
            status["return_code"] = 1
            status["status"] = "failed"
            status["error"] = str(exc)
            stderr_path.write_text(str(exc), encoding="utf-8")

        transformed_path = Path(config["transformed_path"])
        quality_report_path = upload_dir / "reporte_calidad_carga.csv"
        if transformed_path.exists():
            quality_issues = validate_transformed_csv(transformed_path)
            status["quality_issue_count"] = len(quality_issues)
            write_quality_report(quality_report_path, quality_issues)

        downloads = []
        for label, raw_path in config["download_candidates"]:
            path = Path(raw_path)
            if path.exists():
                downloads.append(
                    {
                        "label": label,
                        "relative_path": str(path.relative_to(upload_dir)).replace("\\", "/"),
                    }
                )
        if stdout_path.exists():
            downloads.append({"label": "Salida ETL", "relative_path": "stdout.log"})
        if stderr_path.exists():
            downloads.append({"label": "Errores ETL", "relative_path": "stderr.log"})

        status["downloads"] = downloads
        write_status(status_path, status)

        self.stdout.write(self.style.SUCCESS(f"Carga finalizada: {config['run_id']} ({status['status']})"))
