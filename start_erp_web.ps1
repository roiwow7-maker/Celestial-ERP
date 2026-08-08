$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DjangoRoot = Join-Path $ProjectRoot "Celestial_ERP"
$HostName = if ($env:ERP_HOST) { $env:ERP_HOST } else { "127.0.0.1" }
$Port = if ($env:ERP_PORT) { $env:ERP_PORT } else { "8000" }

Set-Location $DjangoRoot

if (-not $env:ERP_SETTINGS_ENV) {
    $env:ERP_SETTINGS_ENV = "dev"
}

if (-not $env:DJANGO_ALLOWED_HOSTS) {
    $env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
}

if (-not $env:DJANGO_DEBUG) {
    $env:DJANGO_DEBUG = "true"
}

if ($HostName -eq "0.0.0.0" -and $env:DJANGO_DEBUG -eq "true") {
    Write-Warning "Estas levantando el ERP en red con DJANGO_DEBUG=true. Usalo solo en ambiente controlado."
}

python manage.py migrate
python manage.py check

Write-Host ""
Write-Host "Celestial ERP web disponible en: http://$HostName`:$Port/"
Write-Host "Admin Django: http://$HostName`:$Port/admin/"
Write-Host ""

python manage.py runserver "$HostName`:$Port"
