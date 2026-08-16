#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/home/roy/Escritorio/ETL"
LOCK_FILE="${PROJECT_ROOT}/.automatic_backup.lock"
LOG_FILE="${PROJECT_ROOT}/logs/automatic_postgresql_backup.log"

mkdir -p "${PROJECT_ROOT}/logs"
cd "${PROJECT_ROOT}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    printf '%s Backup omitido: ya existe una ejecucion activa.\n' "$(date --iso-8601=seconds)" >>"${LOG_FILE}"
    exit 0
fi

printf '%s Inicio backup automatico.\n' "$(date --iso-8601=seconds)" >>"${LOG_FILE}"
if "${PROJECT_ROOT}/venv/bin/python" Celestial_ERP/manage.py backup_database >>"${LOG_FILE}" 2>&1; then
    printf '%s Backup automatico completado.\n' "$(date --iso-8601=seconds)" >>"${LOG_FILE}"
else
    status=$?
    printf '%s ERROR backup automatico (codigo %s).\n' "$(date --iso-8601=seconds)" "${status}" >>"${LOG_FILE}"
    exit "${status}"
fi
