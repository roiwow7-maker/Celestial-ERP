$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DjangoRoot = Join-Path $ProjectRoot "Celestial_ERP"

Set-Location $DjangoRoot
python manage.py backup_sqlite
