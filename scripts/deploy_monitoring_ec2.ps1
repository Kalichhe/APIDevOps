param(
    [Parameter(Mandatory = $true)]
    [string]$Ec2Host,

    [Parameter(Mandatory = $true)]
    [string]$SshKeyPath,

    [string]$SshUser = "ec2-user",

    [string]$RemotePath = "/home/ec2-user/apidevops-monitoring",

    [Parameter(Mandatory = $true)]
    [string]$ApiTarget,

    [Parameter(Mandatory = $true)]
    [string]$MetricsToken,

    [string]$GrafanaAdminPassword = "admin123"
)

$ErrorActionPreference = "Stop"

function Ensure-CommandExists {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "No se encontro '$Name'. Instala la herramienta antes de continuar."
    }
}

function Invoke-RemoteCommand {
    param([string]$Command)

    # Bash on Linux fails when Windows CRLF is sent over SSH.
    $normalizedCommand = ($Command -replace "`r`n", "`n") -replace "`r", "`n"

    $sshArgs = @(
        "-i", $SshKeyPath,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=15",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=2",
        "$SshUser@$Ec2Host",
        $normalizedCommand
    )

    Write-Host "[remote] Ejecutando comando..." -ForegroundColor DarkGray
    & ssh @sshArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo comando remoto: $normalizedCommand"
    }
    Write-Host "[remote] OK" -ForegroundColor DarkGray
}

function Copy-ToRemote {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    $scpArgs = @(
        "-i", $SshKeyPath,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=15",
        "-r",
        $SourcePath,
        "${SshUser}@${Ec2Host}:${DestinationPath}"
    )

    & scp @scpArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo la copia de $SourcePath a $DestinationPath"
    }
    Write-Host "[scp] Copia completada" -ForegroundColor DarkGray
}

function New-TemporaryWorkspace {
    $tempPath = Join-Path $env:TEMP ("apidevops-monitoring-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tempPath | Out-Null
    return $tempPath
}

Write-Host "== Verificando prerequisitos ==" -ForegroundColor Cyan
Ensure-CommandExists -Name "ssh"
Ensure-CommandExists -Name "scp"

if (-not (Test-Path $SshKeyPath)) {
    throw "No existe la llave SSH: $SshKeyPath"
}

if ([string]::IsNullOrWhiteSpace($ApiTarget)) {
    throw "ApiTarget es obligatorio. Ejemplo: apidevops-prod.eba-xxxx.us-east-2.elasticbeanstalk.com:80"
}
if ([string]::IsNullOrWhiteSpace($MetricsToken)) {
    throw "MetricsToken es obligatorio para scrapear /metrics protegido."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$workspace = New-TemporaryWorkspace

try {
    Write-Host "== Preparando archivos para AWS EC2 ==" -ForegroundColor Cyan

    $prometheusTemplate = Join-Path $repoRoot "prometheus.yml"
    $composeTemplate = Join-Path $repoRoot "docker-compose.monitoring.aws.yml"
    $grafanaSource = Join-Path $repoRoot "grafana"
    $prometheusDestination = Join-Path $workspace "prometheus.yml"
    $composeDestination = Join-Path $workspace "docker-compose.monitoring.aws.yml"
    $grafanaDestination = Join-Path $workspace "grafana"

    if (-not (Test-Path $prometheusTemplate)) {
        throw "No se encontro el archivo de Prometheus: $prometheusTemplate"
    }
    if (-not (Test-Path $composeTemplate)) {
        throw "No se encontro el compose AWS: $composeTemplate"
    }
    if (-not (Test-Path $grafanaSource)) {
        throw "No se encontro la carpeta de Grafana: $grafanaSource"
    }

    $prometheusContent = Get-Content $prometheusTemplate -Raw
    if ($prometheusContent -notmatch 'app:8000') {
        Write-Host "Advertencia: el template de Prometheus no contiene app:8000; se reemplazara de todos modos." -ForegroundColor Yellow
    }
    $prometheusContent = $prometheusContent -replace 'app:8000', $ApiTarget
    $metricsTokenYaml = $MetricsToken -replace "'", "''"
    $prometheusContent = $prometheusContent -replace '__METRICS_TOKEN__', $metricsTokenYaml
    Set-Content -Path $prometheusDestination -Value $prometheusContent -Encoding UTF8

    Copy-Item -Path $composeTemplate -Destination $composeDestination
    Copy-Item -Path $grafanaSource -Destination $grafanaDestination -Recurse -Force

    Write-Host "== Creando directorio remoto ==" -ForegroundColor Cyan
    Write-Host "Ruta remota: $RemotePath" -ForegroundColor DarkCyan
    Invoke-RemoteCommand "echo connected"
    Invoke-RemoteCommand "mkdir -p $RemotePath"

    Write-Host "== Subiendo stack de monitoreo ==" -ForegroundColor Cyan
    Copy-ToRemote -SourcePath (Join-Path $workspace "*") -DestinationPath $RemotePath

    Write-Host "== Iniciando servicios en EC2 ==" -ForegroundColor Cyan
    $grafanaPasswordSafe = $GrafanaAdminPassword -replace "'", "'\''"
    $remoteSetup = @"
cd $RemotePath
echo "[compose] Detectando Docker Compose..."
COMPOSE_V2_OUTPUT=`$(docker compose version 2>/dev/null || true)
if echo "`$COMPOSE_V2_OUTPUT" | grep -qi "Docker Compose"; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo "No se encontro Docker Compose en la instancia" >&2
    exit 1
fi
echo "[compose] Usando: `$COMPOSE_CMD"
GRAFANA_ADMIN_PASSWORD='$grafanaPasswordSafe' `$COMPOSE_CMD -f docker-compose.monitoring.aws.yml up -d
echo "[compose] Servicios levantados"
"@
    Invoke-RemoteCommand $remoteSetup

    Write-Host ""
    Write-Host "Despliegue completado." -ForegroundColor Green
    Write-Host "Grafana: http://$Ec2Host:3000" -ForegroundColor Green
    Write-Host "Prometheus: http://$Ec2Host:9090" -ForegroundColor Green
    Write-Host ""
    Write-Host "Credenciales Grafana por defecto: admin / $GrafanaAdminPassword" -ForegroundColor Cyan
}
finally {
    if (Test-Path $workspace) {
        Remove-Item -Path $workspace -Recurse -Force
    }
}
