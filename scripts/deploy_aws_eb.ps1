param(
    [string]$Region = "us-east-2",
    [string]$AppName = "APIDevOps",
    [string]$EnvironmentName = "apidevops-prod",
    [string]$DbInstanceIdentifier = "apidevops-db",
    [string]$DbName = "postgres",
    [string]$DbUser = "postgres",
    [string]$DbSslMode = "require",
    [string]$DbInstanceClass = "db.t3.micro",
    [int]$DbAllocatedStorage = 20,
    [int]$DbBackupRetentionPeriod = 0,
    [string]$EbPlatform = "Docker"
)

$ErrorActionPreference = "Stop"

function Get-PlainTextFromSecureString {
    param([SecureString]$Secure)
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try {
        return [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    }
    finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Ensure-CommandExists {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "No se encontro '$Name'. Instala la herramienta antes de continuar."
    }
}

function Aws-Json {
    param(
        [string]$Command,
        [switch]$AllowFailure
    )

    try {
        $raw = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -ne 0) {
            if ($AllowFailure) {
                return $null
            }
            throw "Comando AWS fallo: $Command`n$raw"
        }
    }
    catch {
        if ($AllowFailure) {
            return $null
        }
        throw
    }

    if (-not $raw) {
        return $null
    }
    return $raw | ConvertFrom-Json
}

function Invoke-AwsCommand {
    param([string]$Command)

    $result = Invoke-Expression $Command 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Comando AWS/EB fallo: $Command`n$result"
    }
    return $result
}

Write-Host "== Verificando prerequisitos (aws, eb) ==" -ForegroundColor Cyan
Ensure-CommandExists -Name "aws"
Ensure-CommandExists -Name "eb"

Write-Host "== Ingresa solo secretos (se usan en esta sesion) ==" -ForegroundColor Cyan
$AwsAccessKeyId = Read-Host "AWS_ACCESS_KEY_ID"
$AwsSecretSecure = Read-Host "AWS_SECRET_ACCESS_KEY" -AsSecureString
$DbPasswordSecure = Read-Host "POSTGRES_PASSWORD (RDS)" -AsSecureString
$MetricsToken = Read-Host "METRICS_TOKEN (para proteger /metrics, deja vacio para generar)"

$AwsSecretAccessKey = Get-PlainTextFromSecureString -Secure $AwsSecretSecure
$DbPassword = Get-PlainTextFromSecureString -Secure $DbPasswordSecure

if ([string]::IsNullOrWhiteSpace($AwsAccessKeyId) -or [string]::IsNullOrWhiteSpace($AwsSecretAccessKey)) {
    throw "AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY son obligatorios."
}
if ([string]::IsNullOrWhiteSpace($DbPassword)) {
    throw "POSTGRES_PASSWORD es obligatorio."
}

if ([string]::IsNullOrWhiteSpace($MetricsToken)) {
    $MetricsToken = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
    Write-Host "METRICS_TOKEN generado automaticamente." -ForegroundColor Yellow
}

$MetricsTokenSafe = $MetricsToken -replace "'", "''"

$env:AWS_ACCESS_KEY_ID = $AwsAccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $AwsSecretAccessKey
$env:AWS_DEFAULT_REGION = $Region

Write-Host "== Validando credenciales AWS ==" -ForegroundColor Cyan
$caller = Aws-Json "aws sts get-caller-identity --output json"
if (-not $caller) {
    throw "No se pudo validar la identidad AWS."
}
Write-Host "Cuenta AWS detectada: $($caller.Account)" -ForegroundColor Green

Write-Host "== Detectando VPC por defecto y subredes ==" -ForegroundColor Cyan
$defaultVpc = Aws-Json "aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0]' --output json"
if (-not $defaultVpc -or -not $defaultVpc.VpcId) {
    throw "No se encontro VPC por defecto. Crea una o ajusta el script para usar una VPC existente."
}
$vpcId = $defaultVpc.VpcId
$vpcCidr = $defaultVpc.CidrBlock

$subnets = Aws-Json "aws ec2 describe-subnets --filters Name=vpc-id,Values=$vpcId --query 'Subnets[].SubnetId' --output json"
if (-not $subnets -or $subnets.Count -lt 2) {
    throw "Se requieren al menos 2 subredes en la VPC para RDS."
}
$dbSubnetGroupName = "$DbInstanceIdentifier-subnet-group"

Write-Host "== Creando/validando DB Subnet Group ==" -ForegroundColor Cyan
$existingSubnetGroup = Aws-Json "aws rds describe-db-subnet-groups --db-subnet-group-name $dbSubnetGroupName --output json" -AllowFailure
if (-not $existingSubnetGroup) {
    $subnetArgs = ($subnets | ForEach-Object { "'$_'" }) -join " "
    Invoke-AwsCommand "aws rds create-db-subnet-group --db-subnet-group-name $dbSubnetGroupName --db-subnet-group-description 'Subnet group for $DbInstanceIdentifier' --subnet-ids $subnetArgs --output json" | Out-Null
    Write-Host "DB Subnet Group creado: $dbSubnetGroupName" -ForegroundColor Green
} else {
    Write-Host "DB Subnet Group existente: $dbSubnetGroupName" -ForegroundColor Yellow
}

Write-Host "== Creando/validando Security Group para RDS ==" -ForegroundColor Cyan
$rdsSgName = "$DbInstanceIdentifier-rds-sg"
$existingSg = Aws-Json "aws ec2 describe-security-groups --filters Name=group-name,Values=$rdsSgName Name=vpc-id,Values=$vpcId --query 'SecurityGroups[0]' --output json"
if (-not $existingSg -or -not $existingSg.GroupId) {
    $createdSg = Aws-Json "aws ec2 create-security-group --group-name $rdsSgName --description 'RDS access SG for $DbInstanceIdentifier' --vpc-id $vpcId --output json"
    $rdsSgId = $createdSg.GroupId
    Write-Host "Security Group creado: $rdsSgId" -ForegroundColor Green
} else {
    $rdsSgId = $existingSg.GroupId
    Write-Host "Security Group existente: $rdsSgId" -ForegroundColor Yellow
}

$ipPermissions = Aws-Json "aws ec2 describe-security-groups --group-ids $rdsSgId --query 'SecurityGroups[0].IpPermissions' --output json"
$has5432Rule = $false

foreach ($perm in $ipPermissions) {
    if ($perm.IpProtocol -eq "tcp" -and $perm.FromPort -eq 5432 -and $perm.ToPort -eq 5432) {
        foreach ($range in $perm.IpRanges) {
            if ($range.CidrIp -eq $vpcCidr) {
                $has5432Rule = $true
                break
            }
        }
    }
    if ($has5432Rule) {
        break
    }
}

if ($has5432Rule) {
    Write-Host "Regla 5432 ya existia para CIDR VPC $vpcCidr" -ForegroundColor Yellow
}
else {
    Invoke-AwsCommand "aws ec2 authorize-security-group-ingress --group-id $rdsSgId --protocol tcp --port 5432 --cidr $vpcCidr --output json" | Out-Null
    Write-Host "Regla 5432 agregada para CIDR VPC $vpcCidr" -ForegroundColor Green
}

Write-Host "== Creando/validando instancia RDS ==" -ForegroundColor Cyan
$existingDb = Aws-Json "aws rds describe-db-instances --db-instance-identifier $DbInstanceIdentifier --output json" -AllowFailure
if (-not $existingDb) {
    $createDbCmd = @(
        "aws rds create-db-instance",
        "--db-instance-identifier $DbInstanceIdentifier",
        "--db-instance-class $DbInstanceClass",
        "--engine postgres",
        "--allocated-storage $DbAllocatedStorage",
        "--master-username $DbUser",
        "--master-user-password '$DbPassword'",
        "--db-name $DbName",
        "--db-subnet-group-name $dbSubnetGroupName",
        "--vpc-security-group-ids $rdsSgId",
        "--publicly-accessible",
        "--backup-retention-period $DbBackupRetentionPeriod",
        "--storage-type gp3",
        "--no-multi-az",
        "--output json"
    ) -join " "

    Invoke-AwsCommand $createDbCmd | Out-Null
    Write-Host "RDS en creacion: $DbInstanceIdentifier" -ForegroundColor Green
} else {
    Write-Host "RDS existente detectada: $DbInstanceIdentifier" -ForegroundColor Yellow
}

Write-Host "== Esperando RDS disponible (puede tardar varios minutos) ==" -ForegroundColor Cyan
Invoke-AwsCommand "aws rds wait db-instance-available --db-instance-identifier $DbInstanceIdentifier" | Out-Null

$dbInfo = Aws-Json "aws rds describe-db-instances --db-instance-identifier $DbInstanceIdentifier --query 'DBInstances[0]' --output json"
$dbHost = $dbInfo.Endpoint.Address
if (-not $dbHost) {
    throw "No se pudo obtener endpoint de RDS."
}
Write-Host "Endpoint RDS: $dbHost" -ForegroundColor Green

Write-Host "== Creando/validando aplicacion Elastic Beanstalk ==" -ForegroundColor Cyan
$existingApp = Aws-Json "aws elasticbeanstalk describe-applications --application-names $AppName --query 'Applications[0]' --output json"
if (-not $existingApp) {
    Invoke-Expression "aws elasticbeanstalk create-application --application-name $AppName --output json" | Out-Null
    Write-Host "Aplicacion EB creada: $AppName" -ForegroundColor Green
} else {
    Write-Host "Aplicacion EB existente: $AppName" -ForegroundColor Yellow
}

if (-not (Test-Path ".elasticbeanstalk\config.yml")) {
    Write-Host "== Inicializando proyecto para EB ==" -ForegroundColor Cyan
    Invoke-AwsCommand "eb init $AppName --platform '$EbPlatform' --region $Region" | Out-Null
}

$existingEnv = Aws-Json "aws elasticbeanstalk describe-environments --application-name $AppName --environment-names $EnvironmentName --include-deleted --query 'Environments[0]' --output json"
if (-not $existingEnv -or $existingEnv.Status -eq "Terminated") {
    Write-Host "== Creando entorno Elastic Beanstalk ==" -ForegroundColor Cyan
    $createResult = Invoke-Expression "eb create $EnvironmentName --single --instance_type t3.micro" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "eb create devolvio error. Verificando si el entorno fue creado para continuar con setenv/deploy..." -ForegroundColor Yellow
        $createdEnvAfterError = Aws-Json "aws elasticbeanstalk describe-environments --application-name $AppName --environment-names $EnvironmentName --include-deleted --query 'Environments[0]' --output json" -AllowFailure
        if (-not $createdEnvAfterError -or $createdEnvAfterError.Status -eq "Terminated") {
            $createOutputText = $createResult | Out-String
            throw "No se pudo crear el entorno Elastic Beanstalk.`n$createOutputText"
        }
        Write-Host "Entorno creado con estado degradado. Se intentara recuperar aplicando variables y redeploy." -ForegroundColor Yellow
    }
} else {
    Write-Host "Entorno EB existente: $EnvironmentName" -ForegroundColor Yellow
}

Invoke-AwsCommand "eb use $EnvironmentName" | Out-Null

$encodedDbPassword = [System.Uri]::EscapeDataString($DbPassword)
$databaseUrl = "postgresql+psycopg2://${DbUser}:$encodedDbPassword@${dbHost}:5432/${DbName}?sslmode=${DbSslMode}"

Write-Host "== Configurando variables de entorno en EB ==" -ForegroundColor Cyan

# Variables base
$envVars = "POSTGRES_USER=$DbUser POSTGRES_PASSWORD='$DbPassword' POSTGRES_DB=$DbName DATABASE_URL='$databaseUrl' METRICS_TOKEN='$MetricsTokenSafe'"

Invoke-AwsCommand "eb setenv -e $EnvironmentName $envVars" | Out-Null

Write-Host "== Desplegando aplicacion ==" -ForegroundColor Cyan
Invoke-AwsCommand "eb deploy $EnvironmentName" | Out-Null

$envInfo = Aws-Json "aws elasticbeanstalk describe-environments --application-name $AppName --environment-names $EnvironmentName --query 'Environments[0]' --output json"
$cname = $envInfo.CNAME

Write-Host ""
Write-Host "Despliegue finalizado." -ForegroundColor Green
Write-Host "App URL: http://$cname" -ForegroundColor Green
Write-Host "Swagger: http://$cname/docs" -ForegroundColor Green
Write-Host "METRICS_TOKEN (guardalo para Prometheus EC2): $MetricsToken" -ForegroundColor Yellow
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  eb status"
Write-Host "  eb health"
Write-Host "  eb logs"
